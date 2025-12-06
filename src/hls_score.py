"""
Human Legitimacy Score (HLS) Computation Module

This module computes a 0-100 score indicating how likely an EEG signal
is from a genuine human brain versus synthetic/artificial sources.

Components:
    PBD (25%): Physiological Baseline Deviation - variance patterns
    NCM (10%): Neural Complexity Measures - spectral entropy
    MVI (25%): Micro-Variability Index - sample-to-sample variations
    TAM (25%): Temporal Autocorrelation Measures - temporal structure
    NSC (15%): Neural Signal Consistency - cross-channel patterns

Usage:
    >>> from src.hls_score import compute_hls
    >>> scores = compute_hls(data, fs=256.0)
    >>> is_human = scores['hls'] >= 70

Author: EEG Legitimacy Team
"""

import numpy as np
from scipy import signal
from scipy.stats import entropy

# Constants
HUMAN_THRESHOLD = 70  # Score >= 70 indicates human EEG


def compute_pbd(data: np.ndarray) -> float:
    """
    Compute Physiological Baseline Deviation (PBD).
    
    Measures how well the signal conforms to expected physiological baselines.
    Based on variance and amplitude distribution characteristics.
    """
    # Check variance is within physiological range
    variance = np.var(data, axis=0)
    mean_var = np.mean(variance)
    
    # Penalize very low variance (constant signals)
    if mean_var < 0.5:
        return 0.2  # Very low score for near-constant
    
    # Amplitude range check (expect microvolt-level signals)
    amplitude_range = np.ptp(data, axis=0)
    mean_range = np.mean(amplitude_range)
    
    # Score based on variance consistency across channels
    var_consistency = 1.0 - np.std(variance) / (np.mean(variance) + 1e-10)
    var_consistency = np.clip(var_consistency, 0, 1)
    
    # Penalize too-uniform variance (synthetic often has identical channels)
    if np.std(variance) / (np.mean(variance) + 1e-10) < 0.05:
        var_consistency *= 0.5  # Penalize
    
    # Penalize extreme values (too uniform or too variable)
    cv = np.std(data) / (np.mean(np.abs(data)) + 1e-10)
    cv_score = np.exp(-0.5 * ((cv - 1.0) ** 2))  # Optimal CV around 1
    
    return float((var_consistency + cv_score) / 2)


def compute_ncm(data: np.ndarray, fs: float = 256.0) -> float:
    """
    Compute Neural Complexity Measures (NCM).
    
    Combines spectral entropy and fractal characteristics to assess
    neural signal complexity typical of genuine brain activity.
    """
    n_channels = data.shape[1]
    complexity_scores = []
    
    for ch in range(n_channels):
        # Spectral entropy
        freqs, psd = signal.welch(data[:, ch], fs=fs, nperseg=min(256, len(data)))
        psd_norm = psd / (np.sum(psd) + 1e-10)
        spec_ent = entropy(psd_norm) / np.log(len(psd_norm) + 1)
        
        # Genuine EEG has moderate complexity (not too random, not too regular)
        # Optimal spectral entropy around 0.6-0.8
        complexity_score = 1.0 - 2 * np.abs(spec_ent - 0.7)
        complexity_scores.append(np.clip(complexity_score, 0, 1))
    
    return float(np.mean(complexity_scores))


def compute_mvi(data: np.ndarray) -> float:
    """
    Compute Micro-Variability Index (MVI).
    
    Assesses sample-to-sample variations characteristic of biological signals.
    Synthetic signals often lack natural micro-variability patterns.
    """
    # First-order differences
    diff1 = np.diff(data, axis=0)
    micro_var = np.mean(np.abs(diff1), axis=0)
    mean_micro_var = np.mean(micro_var)
    
    # Penalize very low micro-variability (constant or slowly drifting)
    # Threshold lowered to 0.05 to accommodate real EEG at different sampling rates
    if mean_micro_var < 0.05:
        return 0.2
    
    # Second-order differences (acceleration)
    diff2 = np.diff(diff1, axis=0)
    micro_var2 = np.mean(np.abs(diff2), axis=0)
    
    # Ratio of first to second order (biological signals have characteristic ratio)
    ratio = micro_var / (micro_var2 + 1e-10)
    mean_ratio = np.mean(ratio)
    
    # Score based on expected ratio range (typically 1.5-3 for EEG)
    optimal_ratio = 2.0
    ratio_score = np.exp(-0.3 * (mean_ratio - optimal_ratio) ** 2)
    
    # Penalize extreme ratios (synthetic signals often have wrong ratio)
    if mean_ratio < 0.5 or mean_ratio > 5:
        ratio_score *= 0.3
    
    # Check for zero-crossings in differences (should be frequent in real EEG)
    zero_crossings = np.mean([np.sum(np.diff(np.sign(diff1[:, ch])) != 0) 
                              for ch in range(data.shape[1])])
    zc_rate = zero_crossings / len(diff1)
    
    # Penalize too-uniform zero crossing rate (synthetic is often too regular)
    zc_std = np.std([np.sum(np.diff(np.sign(diff1[:, ch])) != 0) / len(diff1)
                     for ch in range(data.shape[1])])
    if zc_std < 0.01:  # Too uniform across channels
        zc_score = 0.3
    else:
        zc_score = np.clip(zc_rate / 0.5, 0, 1)  # Expect ~50% zero-crossing rate
    
    return float((ratio_score + zc_score) / 2)


def compute_tam(data: np.ndarray) -> float:
    """
    Compute Temporal Autocorrelation Measures (TAM).
    
    Genuine EEG exhibits specific autocorrelation patterns reflecting
    underlying neural dynamics. Synthetic signals often fail this test.
    """
    n_channels = data.shape[1]
    tam_scores = []
    
    for ch in range(n_channels):
        x = data[:, ch]
        x = x - np.mean(x)
        
        # Compute autocorrelation at multiple lags
        max_lag = min(50, len(x) // 4)
        autocorr = np.correlate(x, x, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / (autocorr[0] + 1e-10)
        
        # Check decay pattern (should decay but not too fast)
        if len(autocorr) > max_lag:
            decay_rate = -np.polyfit(np.arange(max_lag), 
                                     np.log(np.abs(autocorr[:max_lag]) + 1e-10), 1)[0]
            # Optimal decay rate for EEG around 0.02-0.1
            decay_score = np.exp(-5 * (decay_rate - 0.05) ** 2)
            tam_scores.append(np.clip(decay_score, 0, 1))
    
    return float(np.mean(tam_scores)) if tam_scores else 0.5


def compute_nsc(data: np.ndarray, fs: float = 256.0) -> float:
    """
    Compute Neural Signal Consistency (NSC).
    
    Measures cross-channel consistency and physiological frequency band
    presence expected in genuine neural recordings.
    """
    n_channels = data.shape[1]
    
    # Cross-channel correlation (genuine EEG has moderate inter-channel correlation)
    if n_channels > 1:
        corr_matrix = np.corrcoef(data.T)
        upper_tri = corr_matrix[np.triu_indices(n_channels, k=1)]
        mean_corr = np.mean(np.abs(upper_tri))
        
        # Heavily penalize very high correlation (>0.95 = likely correlated noise)
        if mean_corr > 0.95:
            corr_score = 0.1
        # Penalize very low correlation (<0.05 = likely independent noise)
        elif mean_corr < 0.05:
            corr_score = 0.3
        else:
            # Real EEG has correlation ranging 0.2-0.8 depending on montage
            # Center around 0.5 with wider tolerance
            corr_score = 1.0 - 1.5 * np.abs(mean_corr - 0.5)
            corr_score = np.clip(corr_score, 0.3, 1)
    else:
        corr_score = 0.5
    
    # Check for presence of physiological frequency bands
    band_scores = []
    for ch in range(min(n_channels, 5)):  # Sample up to 5 channels
        freqs, psd = signal.welch(data[:, ch], fs=fs, nperseg=min(256, len(data)))
        
        # Define frequency bands
        delta = (0.5, 4)
        theta = (4, 8)
        alpha = (8, 13)
        beta = (13, 30)
        
        total_power = np.sum(psd)
        bands_present = 0
        for band in [delta, theta, alpha, beta]:
            band_mask = (freqs >= band[0]) & (freqs <= band[1])
            band_power = np.sum(psd[band_mask]) / (total_power + 1e-10)
            # Each band should have some power (0.05-0.4)
            if 0.05 < band_power < 0.4:
                bands_present += 1
        
        # Score based on how many bands are present (need at least 2-3)
        band_scores.append(bands_present / 4.0)
    
    band_score = np.mean(band_scores) if band_scores else 0.0
    
    # Penalize if no proper band structure
    if band_score < 0.25:
        band_score = 0.1
    
    return float((corr_score + band_score) / 2)


def compute_hls(
    data: np.ndarray,
    fs: float = 256.0,
    weights: dict[str, float] | None = None
) -> dict[str, float]:
    """
    Compute the Human Legitimacy Score (HLS).
    
    Combines five feature groups into a final 0-100 score indicating
    how likely the EEG signal is from a genuine human source.
    
    Parameters
    ----------
    data : np.ndarray
        2D array of shape (n_samples, n_channels).
    fs : float, optional
        Sampling frequency in Hz. Default is 256 Hz.
    weights : dict[str, float], optional
        Custom weights for each component. Default is equal weighting.
    
    Returns
    -------
    dict[str, float]
        Dictionary containing:
        - 'hls': Final Human Legitimacy Score (0-100)
        - 'pbd': Physiological Baseline Deviation score (0-1)
        - 'ncm': Neural Complexity Measures score (0-1)
        - 'mvi': Micro-Variability Index score (0-1)
        - 'tam': Temporal Autocorrelation Measures score (0-1)
        - 'nsc': Neural Signal Consistency score (0-1)
    
    Example
    -------
    >>> from src.loader import load_eeg_csv
    >>> time, data, channels = load_eeg_csv("data/sample.csv")
    >>> scores = compute_hls(data, fs=256.0)
    >>> print(f"Human Legitimacy Score: {scores['hls']:.1f}/100")
    """
    if weights is None:
        weights = {
            "pbd": 0.25,  # Physiological Baseline - important
            "ncm": 0.10,  # Neural Complexity - reduced weight
            "mvi": 0.25,  # Micro-Variability - important
            "tam": 0.25,  # Temporal Autocorrelation - important
            "nsc": 0.15,
        }
    
    # Compute individual components
    pbd = compute_pbd(data)
    ncm = compute_ncm(data, fs)
    mvi = compute_mvi(data)
    tam = compute_tam(data)
    nsc = compute_nsc(data, fs)
    
    # Weighted combination
    combined = (
        weights["pbd"] * pbd +
        weights["ncm"] * ncm +
        weights["mvi"] * mvi +
        weights["tam"] * tam +
        weights["nsc"] * nsc
    )
    
    # Scale to 0-100
    hls = combined * 100
    
    return {
        "hls": float(np.clip(hls, 0, 100)),
        "pbd": float(pbd),
        "ncm": float(ncm),
        "mvi": float(mvi),
        "tam": float(tam),
        "nsc": float(nsc),
    }

