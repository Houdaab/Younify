"""
EEG data loader module.

Supports:
- CSV files (with Time column)
- EDF/BDF files (European Data Format - used by OpenNeuro)
- BIDS format (extracts subject IDs from file paths)
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from typing import Optional, Dict


def load_eeg_edf(filepath: str | Path, duration: float | None = None) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Load EEG data from EDF/BDF file (OpenNeuro, clinical EEG).
    
    Parameters
    ----------
    filepath : str or Path
        Path to the EDF/BDF file.
    duration : float, optional
        Max duration in seconds to load. None = load all.
    
    Returns
    -------
    tuple[np.ndarray, np.ndarray, list[str]]
        - time: 1D array of time values
        - data: 2D array of shape (n_samples, n_channels)
        - channels: list of channel names
    
    Example
    -------
    >>> time, data, channels = load_eeg_edf("data/subject01.edf")
    """
    try:
        import mne
    except ImportError:
        raise ImportError("MNE package required for EDF files. Install with: pip install mne")
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Load EDF file
    raw = mne.io.read_raw_edf(str(filepath), preload=True, verbose=False)
    
    # Get data
    if duration:
        raw = raw.crop(tmax=duration)
    
    data = raw.get_data().T  # Shape: (n_samples, n_channels)
    channels = raw.ch_names
    sfreq = raw.info['sfreq']
    
    # Create time array
    n_samples = data.shape[0]
    time = np.arange(n_samples) / sfreq
    
    return time, data, channels


def load_eeg_auto(filepath: str | Path, **kwargs) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Auto-detect file format and load EEG data.
    
    Supports: .csv, .edf, .bdf
    """
    filepath = Path(filepath)
    suffix = filepath.suffix.lower()
    
    if suffix == '.csv':
        return load_eeg_csv(filepath)
    elif suffix in ['.edf', '.bdf']:
        return load_eeg_edf(filepath, **kwargs)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv, .edf, or .bdf")


def extract_subject_id(filepath: str | Path) -> Optional[str]:
    """
    Extract subject ID from BIDS format file path.
    
    BIDS format: sub-<label> (e.g., sub-001, sub-002)
    
    Parameters
    ----------
    filepath : str or Path
        Path to the EEG file
        
    Returns
    -------
    str or None
        Subject ID (e.g., "sub-001") or None if not found
        
    Examples
    --------
    >>> extract_subject_id("data/openneuro/ds004504/sub-001/eeg/sub-001_task-rest_eeg.edf")
    'sub-001'
    >>> extract_subject_id("data/sample.csv")
    None
    """
    filepath = Path(filepath)
    path_str = str(filepath)
    
    # BIDS format: sub-<label>
    match = re.search(r'sub-(\w+)', path_str)
    if match:
        return f"sub-{match.group(1)}"
    
    return None


def extract_dataset_id(filepath: str | Path) -> Optional[str]:
    """
    Extract dataset ID from file path.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the EEG file
        
    Returns
    -------
    str or None
        Dataset ID (e.g., "ds004504") or None if not found
        
    Examples
    --------
    >>> extract_dataset_id("data/openneuro/ds004504/sub-001/eeg/sub-001_task-rest_eeg.edf")
    'ds004504'
    >>> extract_dataset_id("data/sample.csv")
    None
    """
    filepath = Path(filepath)
    path_str = str(filepath)
    
    # Look for dataset ID pattern: ds followed by digits
    match = re.search(r'ds(\d+)', path_str)
    if match:
        return f"ds{match.group(1)}"
    
    return None


def create_global_subject_id(filepath: str | Path, dataset_id: Optional[str] = None) -> Optional[str]:
    """
    Create a globally unique subject ID across datasets.
    
    Format: <dataset_id>_<subject_id> (e.g., "ds004504_sub-001")
    
    This ensures subject IDs are unique across different datasets, since
    BIDS subject IDs are dataset-specific (sub-001 in ds003775 is different
    from sub-001 in ds004504).
    
    Parameters
    ----------
    filepath : str or Path
        Path to the EEG file
    dataset_id : str, optional
        Dataset ID. If None, extracted from filepath.
        
    Returns
    -------
    str or None
        Globally unique subject ID or None if components not found
        
    Examples
    --------
    >>> create_global_subject_id("data/openneuro/ds004504/sub-001/eeg/sub-001_task-rest_eeg.edf")
    'ds004504_sub-001'
    >>> create_global_subject_id("data/openneuro/ds003775/sub-001/eeg/sub-001_task-rest_eeg.edf")
    'ds003775_sub-001'
    """
    if dataset_id is None:
        dataset_id = extract_dataset_id(filepath)
    
    subject_id = extract_subject_id(filepath)
    
    if dataset_id and subject_id:
        return f"{dataset_id}_{subject_id}"
    elif subject_id:
        # Fallback: use just subject_id if no dataset_id found
        return subject_id
    
    return None


def load_participants_metadata(dataset_dir: str | Path) -> Optional[pd.DataFrame]:
    """
    Load participants.tsv metadata from BIDS dataset.
    
    Parameters
    ----------
    dataset_dir : str or Path
        Path to BIDS dataset root directory
        
    Returns
    -------
    pd.DataFrame or None
        Participants metadata with subject IDs as index, or None if not found
    """
    dataset_dir = Path(dataset_dir)
    participants_file = dataset_dir / "participants.tsv"
    
    if participants_file.exists():
        try:
            df = pd.read_csv(participants_file, sep='\t')
            # Set participant_id as index if it exists
            if 'participant_id' in df.columns:
                df = df.set_index('participant_id')
            return df
        except Exception as e:
            print(f"Warning: Could not load participants.tsv: {e}")
            return None
    
    return None


def load_eeg_csv(filepath: str | Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Load EEG data from a CSV file.
    
    Expects a CSV with a 'Time' column and one or more EEG channel columns.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the CSV file.
    
    Returns
    -------
    tuple[np.ndarray, np.ndarray, list[str]]
        - time: 1D array of time values
        - data: 2D array of shape (n_samples, n_channels)
        - channels: list of channel names
    
    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the CSV does not contain a 'Time' column.
    
    Example
    -------
    >>> time, data, channels = load_eeg_csv("data/sample.csv")
    >>> print(f"Loaded {len(channels)} channels, {len(time)} samples")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Find the time column (case-insensitive)
    time_col = None
    for col in df.columns:
        if col.lower() == 'time':
            time_col = col
            break
    
    if time_col is None:
        raise ValueError("CSV must contain a 'Time' column")
    
    # Extract time array
    time = df[time_col].to_numpy()
    
    # Get channel columns (all columns except time)
    channels = [col for col in df.columns if col != time_col]
    
    # Extract data as 2D array (samples x channels)
    data = df[channels].to_numpy()
    
    return time, data, channels


def load_eeg_with_metadata(
    filepath: str | Path,
    dataset_dir: Optional[str | Path] = None,
    **kwargs
) -> tuple[np.ndarray, np.ndarray, list[str], Dict]:
    """
    Load EEG data with subject metadata.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the EEG file
    dataset_dir : str or Path, optional
        Path to BIDS dataset root (for loading participants.tsv)
    **kwargs
        Additional arguments passed to load_eeg_auto
        
    Returns
    -------
    tuple
        - time: 1D array of time values
        - data: 2D array of shape (n_samples, n_channels)
        - channels: list of channel names
        - metadata: dict with subject_id, and other metadata from participants.tsv
        
    Example
    -------
    >>> time, data, channels, metadata = load_eeg_with_metadata(
    ...     "data/openneuro/ds004504/sub-001/eeg/sub-001_task-rest_eeg.edf",
    ...     dataset_dir="data/openneuro/ds004504"
    ... )
    >>> print(metadata["subject_id"])  # "sub-001"
    """
    # Load EEG data
    time, data, channels = load_eeg_auto(filepath, **kwargs)
    
    # Extract subject IDs (both local and global)
    subject_id = extract_subject_id(filepath)  # Dataset-specific (e.g., "sub-001")
    dataset_id = extract_dataset_id(filepath)  # Dataset ID (e.g., "ds004504")
    global_subject_id = create_global_subject_id(filepath, dataset_id)  # Globally unique
    
    # Build metadata dictionary
    metadata = {
        "subject_id": subject_id,  # Dataset-specific ID
        "global_subject_id": global_subject_id,  # Globally unique ID
        "dataset_id": dataset_id,  # Dataset identifier
        "filepath": str(filepath),
        "filename": Path(filepath).name,
    }
    
    # Load participants metadata if dataset_dir is provided
    if dataset_dir:
        participants_df = load_participants_metadata(dataset_dir)
        if participants_df is not None and subject_id:
            # Get subject metadata from participants.tsv
            if subject_id in participants_df.index:
                subject_metadata = participants_df.loc[subject_id].to_dict()
                metadata.update(subject_metadata)
    
    return time, data, channels, metadata

