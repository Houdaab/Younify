"""
EEG data loader module.

Supports:
- CSV files (with Time column)
- EDF/BDF files (European Data Format - used by OpenNeuro)
"""

import pandas as pd
import numpy as np
from pathlib import Path


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

