"""
EEG preprocessing module.
"""

import numpy as np


def normalize_channels(data: np.ndarray, method: str = "zscore") -> np.ndarray:
    """
    Normalize EEG data channel-wise.
    
    Parameters
    ----------
    data : np.ndarray
        2D array of shape (n_samples, n_channels).
    method : str, optional
        Normalization method. Options:
        - "zscore": Zero mean, unit variance (default)
        - "minmax": Scale to [0, 1] range
    
    Returns
    -------
    np.ndarray
        Normalized data with same shape as input.
    
    Raises
    ------
    ValueError
        If method is not recognized or data is not 2D.
    
    Example
    -------
    >>> from src.loader import load_eeg_csv
    >>> time, data, channels = load_eeg_csv("data/sample.csv")
    >>> normalized = normalize_channels(data, method="zscore")
    """
    if data.ndim != 2:
        raise ValueError(f"Expected 2D array, got {data.ndim}D")
    
    if method == "zscore":
        mean = np.mean(data, axis=0, keepdims=True)
        std = np.std(data, axis=0, keepdims=True)
        # Avoid division by zero for constant channels
        std = np.where(std == 0, 1, std)
        return (data - mean) / std
    
    elif method == "minmax":
        min_val = np.min(data, axis=0, keepdims=True)
        max_val = np.max(data, axis=0, keepdims=True)
        range_val = max_val - min_val
        # Avoid division by zero for constant channels
        range_val = np.where(range_val == 0, 1, range_val)
        return (data - min_val) / range_val
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'zscore' or 'minmax'.")

