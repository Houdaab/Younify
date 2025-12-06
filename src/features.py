"""
EEG feature extraction module.
"""

import numpy as np
from scipy import signal
from scipy.stats import entropy


def compute_variance(data: np.ndarray) -> np.ndarray:
    """
    Compute variance for each channel.
    
    Parameters
    ----------
    data : np.ndarray
        2D array of shape (n_samples, n_channels).
    
    Returns
    -------
    np.ndarray
        1D array of variance values per channel.
    """
    return np.var(data, axis=0)


def compute_spectral_entropy(data: np.ndarray, fs: float = 256.0) -> np.ndarray:
    """
    Compute spectral entropy for each channel.
    
    Spectral entropy measures the complexity/irregularity of the frequency
    distribution. Higher values indicate more uniform power distribution.
    
    Parameters
    ----------
    data : np.ndarray
        2D array of shape (n_samples, n_channels).
    fs : float, optional
        Sampling frequency in Hz. Default is 256 Hz.
    
    Returns
    -------
    np.ndarray
        1D array of spectral entropy values per channel.
    """
    n_channels = data.shape[1]
    spectral_ent = np.zeros(n_channels)
    
    for ch in range(n_channels):
        # Compute power spectral density
        freqs, psd = signal.welch(data[:, ch], fs=fs, nperseg=min(256, len(data[:, ch])))
        
        # Normalize PSD to get probability distribution
        psd_norm = psd / np.sum(psd)
        
        # Compute entropy (normalized by max possible entropy)
        spectral_ent[ch] = entropy(psd_norm) / np.log(len(psd_norm))
    
    return spectral_ent


def compute_fractal_dimension(data: np.ndarray, kmax: int = 10) -> np.ndarray:
    """
    Compute Higuchi fractal dimension for each channel.
    
    The fractal dimension measures signal complexity. Values typically
    range from 1 (smooth) to 2 (highly complex/space-filling).
    
    Parameters
    ----------
    data : np.ndarray
        2D array of shape (n_samples, n_channels).
    kmax : int, optional
        Maximum delay/interval. Default is 10.
    
    Returns
    -------
    np.ndarray
        1D array of fractal dimension values per channel.
    """
    n_channels = data.shape[1]
    fd = np.zeros(n_channels)
    
    for ch in range(n_channels):
        fd[ch] = _higuchi_fd(data[:, ch], kmax)
    
    return fd


def _higuchi_fd(x: np.ndarray, kmax: int) -> float:
    """
    Compute Higuchi fractal dimension for a single time series.
    """
    n = len(x)
    lk = np.zeros(kmax)
    
    for k in range(1, kmax + 1):
        lm = np.zeros(k)
        for m in range(1, k + 1):
            # Construct subsequence
            indices = np.arange(m - 1, n, k)
            if len(indices) < 2:
                continue
            subsequence = x[indices]
            
            # Compute length of curve
            diff_sum = np.sum(np.abs(np.diff(subsequence)))
            norm_factor = (n - 1) / (k * ((n - m) // k) * k)
            lm[m - 1] = diff_sum * norm_factor
        
        lk[k - 1] = np.mean(lm[lm > 0]) if np.any(lm > 0) else 0
    
    # Linear regression of log(L(k)) vs log(1/k)
    k_vals = np.arange(1, kmax + 1)
    valid = lk > 0
    if np.sum(valid) < 2:
        return 1.0
    
    log_k = np.log(1.0 / k_vals[valid])
    log_lk = np.log(lk[valid])
    
    # Slope of linear fit is fractal dimension
    slope, _ = np.polyfit(log_k, log_lk, 1)
    return slope


def compute_micro_variability(data: np.ndarray) -> np.ndarray:
    """
    Compute micro-variability for each channel.
    
    Micro-variability is the mean absolute difference between consecutive
    samples, capturing high-frequency fluctuations in the signal.
    
    Parameters
    ----------
    data : np.ndarray
        2D array of shape (n_samples, n_channels).
    
    Returns
    -------
    np.ndarray
        1D array of micro-variability values per channel.
    """
    return np.mean(np.abs(np.diff(data, axis=0)), axis=0)


def extract_all_features(data: np.ndarray, fs: float = 256.0) -> dict[str, np.ndarray]:
    """
    Extract all features for each channel.
    
    Parameters
    ----------
    data : np.ndarray
        2D array of shape (n_samples, n_channels).
    fs : float, optional
        Sampling frequency in Hz. Default is 256 Hz.
    
    Returns
    -------
    dict[str, np.ndarray]
        Dictionary with feature names as keys and 1D arrays of values per channel.
    
    Example
    -------
    >>> from src.loader import load_eeg_csv
    >>> time, data, channels = load_eeg_csv("data/sample.csv")
    >>> features = extract_all_features(data, fs=256.0)
    >>> print(features.keys())
    dict_keys(['variance', 'spectral_entropy', 'fractal_dimension', 'micro_variability'])
    """
    return {
        "variance": compute_variance(data),
        "spectral_entropy": compute_spectral_entropy(data, fs),
        "fractal_dimension": compute_fractal_dimension(data),
        "micro_variability": compute_micro_variability(data),
    }

