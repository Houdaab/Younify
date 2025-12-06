"""
Human Legitimacy Score (HLS) Computation Module

Computes a 0-100 score indicating if an EEG signal is from a real human brain.

Key discriminators:
1. 1/f Spectral Slope: Real EEG follows a 1/f power law (slope -1 to -2.5)
2. Spectral Entropy: Real EEG has moderate complexity
3. Channel Uniqueness: Real EEG channels are correlated but not identical

Usage:
    >>> from src.hls_score import compute_hls
    >>> scores = compute_hls(data, fs=500.0)
    >>> is_human = scores['hls'] >= 50
"""

import numpy as np
from scipy import signal
from scipy.stats import entropy

HUMAN_THRESHOLD = 50


def compute_spectral_slope(data: np.ndarray, fs: float) -> float:
    """
    Compute 1/f spectral slope - KEY DISCRIMINATOR.
    
    Real EEG has characteristic 1/f (pink noise) spectrum with slope -1 to -2.5.
    White noise: slope ~ 0
    Synthetic sine waves: slope << -3 (too steep)
    """
    n_samples = len(data)
    nperseg = min(512, n_samples // 4)
    if nperseg < 64:
        nperseg = 64
    
    freqs, psd = signal.welch(data, fs=fs, nperseg=nperseg)
    
    # Fit in 1-30 Hz range (typical EEG range)
    mask = (freqs >= 1) & (freqs <= 30)
    if np.sum(mask) < 5:
        return 0.0
    
    log_f = np.log10(freqs[mask])
    log_p = np.log10(psd[mask] + 1e-20)
    
    # Linear fit in log-log space
    slope, _ = np.polyfit(log_f, log_p, 1)
    return slope


def compute_slope_score(data: np.ndarray, fs: float) -> float:
    """
    Score based on 1/f spectral slope.
    
    Optimal: slope in range [-2.5, -0.8]
    Penalize: slope near 0 (noise) or < -3 (synthetic sines)
    """
    n_channels = data.shape[1] if data.ndim > 1 else 1
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    
    slopes = []
    for ch in range(min(10, n_channels)):
        slope = compute_spectral_slope(data[:, ch], fs)
        slopes.append(slope)
    
    mean_slope = np.mean(slopes)
    
    # Score based on slope value
    # Real EEG: -0.8 to -2.5
    if -2.5 <= mean_slope <= -0.8:
        # Optimal range - full score
        score = 1.0
    elif -3.5 <= mean_slope < -2.5:
        # Slightly too steep but acceptable
        score = 0.7
    elif -0.8 < mean_slope <= 0.3:
        # Too flat (noise-like) - penalize
        score = 0.3 - (mean_slope + 0.8) * 0.2
    elif mean_slope > 0.3:
        # Positive slope (very wrong)
        score = 0.1
    else:
        # Very steep (< -3.5, synthetic sines)
        score = max(0.1, 0.5 + (mean_slope + 3.5) * 0.3)
    
    return float(np.clip(score, 0, 1))


def compute_spectral_entropy_score(data: np.ndarray, fs: float) -> float:
    """
    Score based on spectral entropy.
    
    Real EEG: moderate entropy (0.3-0.75)
    Synthetic noise: high entropy (>0.9)
    Synthetic sine: low entropy (<0.2)
    """
    n_channels = data.shape[1] if data.ndim > 1 else 1
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    
    scores = []
    for ch in range(min(10, n_channels)):
        n_samples = len(data)
        nperseg = min(512, n_samples // 4)
        if nperseg < 64:
            nperseg = 64
        
        freqs, psd = signal.welch(data[:, ch], fs=fs, nperseg=nperseg)
        psd_norm = psd / (np.sum(psd) + 1e-10)
        spec_ent = entropy(psd_norm) / (np.log(len(psd_norm)) + 1e-10)
        
        # Score
        if 0.3 <= spec_ent <= 0.75:
            score = 1.0
        elif spec_ent < 0.2:
            score = spec_ent * 3  # 0-0.6
        elif spec_ent > 0.9:
            score = (1 - spec_ent) * 5  # 0-0.5
        else:
            score = 0.7
        
        scores.append(score)
    
    return float(np.mean(scores))


def compute_channel_uniqueness(data: np.ndarray) -> float:
    """
    Check if channels are unique (not identical).
    """
    n_channels = data.shape[1] if data.ndim > 1 else 1
    if n_channels < 2:
        return 0.5
    
    correlations = []
    for i in range(min(10, n_channels)):
        for j in range(i + 1, min(10, n_channels)):
            corr = np.corrcoef(data[:, i], data[:, j])[0, 1]
            if not np.isnan(corr):
                correlations.append(abs(corr))
    
    if not correlations:
        return 0.5
    
    max_corr = np.max(correlations)
    mean_corr = np.mean(correlations)
    
    # Penalize identical channels
    if max_corr > 0.99:
        return 0.05
    elif max_corr > 0.95:
        return 0.2
    elif mean_corr > 0.9:
        return 0.3
    elif mean_corr < 0.05:
        return 0.4
    else:
        return min(1.0, 0.5 + (1 - mean_corr) * 0.5)


def compute_temporal_structure(data: np.ndarray) -> float:
    """
    Check for natural temporal autocorrelation.
    """
    n_channels = data.shape[1] if data.ndim > 1 else 1
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    
    scores = []
    for ch in range(min(5, n_channels)):
        x = data[:, ch]
        x = x - np.mean(x)
        
        if np.var(x) < 1e-10 or len(x) < 10:
            scores.append(0.3)
            continue
        
        # Autocorrelation at lag 1
        ac1 = np.corrcoef(x[:-1], x[1:])[0, 1]
        if np.isnan(ac1):
            ac1 = 0
        
        # Real EEG: moderate autocorrelation
        if 0.3 < abs(ac1) < 0.95:
            score = 1.0
        elif abs(ac1) < 0.1:
            score = 0.3
        elif abs(ac1) > 0.98:
            score = 0.4
        else:
            score = 0.7
        
        scores.append(score)
    
    return float(np.mean(scores)) if scores else 0.5


def compute_hls(
    data: np.ndarray,
    fs: float = 256.0,
    weights: dict[str, float] | None = None
) -> dict[str, float]:
    """
    Compute the Human Legitimacy Score (HLS).
    
    Parameters
    ----------
    data : np.ndarray
        EEG data, shape (n_samples,) or (n_samples, n_channels)
    fs : float
        Sampling frequency in Hz
    
    Returns
    -------
    dict with 'hls' (0-100) and component scores
    """
    # Ensure 2D
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    
    # Transpose if needed (want samples x channels)
    if data.shape[0] < data.shape[1]:
        data = data.T
    
    if weights is None:
        weights = {
            "slope": 0.40,  # 1/f spectral slope - PRIMARY
            "entropy": 0.25,  # Spectral entropy
            "nsc": 0.20,  # Channel uniqueness
            "tam": 0.15,  # Temporal structure
        }
    
    # Compute components
    slope_score = compute_slope_score(data, fs)
    entropy_score = compute_spectral_entropy_score(data, fs)
    nsc = compute_channel_uniqueness(data)
    tam = compute_temporal_structure(data)
    
    # Weighted combination
    combined = (
        weights["slope"] * slope_score +
        weights["entropy"] * entropy_score +
        weights["nsc"] * nsc +
        weights["tam"] * tam
    )
    
    hls = combined * 100
    
    return {
        "hls": float(np.clip(hls, 0, 100)),
        "pbd": float(slope_score),
        "ncm": float(entropy_score),
        "mvi": float(slope_score),
        "tam": float(tam),
        "nsc": float(nsc),
        "slope": float(slope_score),
        "entropy": float(entropy_score),
    }


def is_human(data: np.ndarray, fs: float = 256.0) -> bool:
    """Quick check if EEG is from a human."""
    return compute_hls(data, fs)["hls"] >= HUMAN_THRESHOLD
