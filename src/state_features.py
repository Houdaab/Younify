"""
EEG State Feature Extraction Module

Extracts features for physiological state classification:
- Per-channel features: mean, std, slope, entropy
- Global features: coherence, variability, occipital activation
"""

import numpy as np
from scipy import signal, stats
from scipy.stats import entropy as scipy_entropy


# Channel groups for analysis
OCCIPITAL_CHANNELS = ["PO3", "PO4", "O1", "O2"]
CENTRAL_CHANNELS = ["C3", "C4"]
PARIETAL_CHANNELS = ["P3", "P4"]


def compute_channel_mean(data: np.ndarray) -> np.ndarray:
    """Compute mean for each channel."""
    return np.mean(data, axis=0)


def compute_channel_std(data: np.ndarray) -> np.ndarray:
    """Compute standard deviation for each channel."""
    return np.std(data, axis=0)


def compute_channel_slope(data: np.ndarray) -> np.ndarray:
    """
    Compute linear slope/trend for each channel.
    Positive slope = increasing trend, negative = decreasing.
    """
    n_samples, n_channels = data.shape
    slopes = np.zeros(n_channels)
    x = np.arange(n_samples)
    
    for ch in range(n_channels):
        slope, _ = np.polyfit(x, data[:, ch], 1)
        slopes[ch] = slope
    
    return slopes


def compute_channel_entropy(data: np.ndarray, bins: int = 20) -> np.ndarray:
    """
    Compute entropy/complexity for each channel using histogram-based entropy.
    Higher entropy = more complex/irregular signal.
    """
    n_channels = data.shape[1]
    entropies = np.zeros(n_channels)
    
    for ch in range(n_channels):
        hist, _ = np.histogram(data[:, ch], bins=bins, density=True)
        hist = hist[hist > 0]  # Remove zeros
        entropies[ch] = scipy_entropy(hist)
    
    return entropies


def compute_channel_range(data: np.ndarray) -> np.ndarray:
    """Compute peak-to-peak range for each channel."""
    return np.ptp(data, axis=0)


def compute_channel_skewness(data: np.ndarray) -> np.ndarray:
    """Compute skewness for each channel."""
    return stats.skew(data, axis=0)


def compute_channel_kurtosis(data: np.ndarray) -> np.ndarray:
    """Compute kurtosis for each channel."""
    return stats.kurtosis(data, axis=0)


def compute_inter_channel_coherence(data: np.ndarray) -> float:
    """
    Compute global inter-channel coherence.
    High coherence = synchronized activity across channels.
    """
    n_channels = data.shape[1]
    if n_channels < 2:
        return 0.0
    
    # Compute correlation matrix
    corr_matrix = np.corrcoef(data.T)
    
    # Get upper triangle (excluding diagonal)
    upper_tri = corr_matrix[np.triu_indices(n_channels, k=1)]
    
    # Mean absolute correlation as coherence measure
    coherence = np.mean(np.abs(upper_tri))
    
    return float(coherence)


def compute_global_variability(data: np.ndarray) -> float:
    """
    Compute global variability across all channels.
    Measures overall signal fluctuation.
    """
    # Mean of channel standard deviations
    channel_stds = np.std(data, axis=0)
    return float(np.mean(channel_stds))


def compute_occipital_activation(data: np.ndarray, channels: list[str]) -> dict:
    """
    Compute occipital region activation metrics.
    High occipital activation often indicates visual processing.
    
    Returns dict with:
    - occipital_power: mean power in occipital channels
    - occipital_ratio: ratio of occipital to non-occipital power
    """
    occipital_indices = [i for i, ch in enumerate(channels) if ch in OCCIPITAL_CHANNELS]
    non_occipital_indices = [i for i, ch in enumerate(channels) if ch not in OCCIPITAL_CHANNELS]
    
    if not occipital_indices:
        return {"occipital_power": 0.0, "occipital_ratio": 0.0}
    
    # Compute power (variance) for occipital channels
    occipital_power = np.mean(np.var(data[:, occipital_indices], axis=0))
    
    if non_occipital_indices:
        non_occipital_power = np.mean(np.var(data[:, non_occipital_indices], axis=0))
        occipital_ratio = occipital_power / (non_occipital_power + 1e-10)
    else:
        occipital_ratio = 1.0
    
    return {
        "occipital_power": float(occipital_power),
        "occipital_ratio": float(occipital_ratio)
    }


def compute_central_activation(data: np.ndarray, channels: list[str]) -> float:
    """
    Compute central region (C3, C4) activation.
    Related to motor/sensorimotor processing.
    """
    central_indices = [i for i, ch in enumerate(channels) if ch in CENTRAL_CHANNELS]
    
    if not central_indices:
        return 0.0
    
    return float(np.mean(np.var(data[:, central_indices], axis=0)))


def compute_parietal_activation(data: np.ndarray, channels: list[str]) -> float:
    """
    Compute parietal region (P3, P4) activation.
    Related to attention and spatial processing.
    """
    parietal_indices = [i for i, ch in enumerate(channels) if ch in PARIETAL_CHANNELS]
    
    if not parietal_indices:
        return 0.0
    
    return float(np.mean(np.var(data[:, parietal_indices], axis=0)))


def compute_asymmetry(data: np.ndarray, channels: list[str]) -> dict:
    """
    Compute left-right hemispheric asymmetry.
    Asymmetry can indicate different cognitive states.
    """
    left_channels = ["C3", "P3", "PO3", "O1"]
    right_channels = ["C4", "P4", "PO4", "O2"]
    
    left_indices = [i for i, ch in enumerate(channels) if ch in left_channels]
    right_indices = [i for i, ch in enumerate(channels) if ch in right_channels]
    
    if not left_indices or not right_indices:
        return {"asymmetry": 0.0, "asymmetry_direction": "balanced"}
    
    left_power = np.mean(np.var(data[:, left_indices], axis=0))
    right_power = np.mean(np.var(data[:, right_indices], axis=0))
    
    # Asymmetry index: positive = right dominant, negative = left dominant
    asymmetry = (right_power - left_power) / (right_power + left_power + 1e-10)
    
    if asymmetry > 0.1:
        direction = "right_dominant"
    elif asymmetry < -0.1:
        direction = "left_dominant"
    else:
        direction = "balanced"
    
    return {
        "asymmetry": float(asymmetry),
        "asymmetry_direction": direction
    }


def compute_signal_stability(data: np.ndarray) -> float:
    """
    Compute signal stability (inverse of sample-to-sample variability).
    High stability = calm/steady state, low = active/changing.
    """
    diff = np.diff(data, axis=0)
    micro_var = np.mean(np.abs(diff))
    
    # Invert and normalize to 0-1 range (higher = more stable)
    stability = 1.0 / (1.0 + micro_var)
    return float(stability)


def extract_state_features(data: np.ndarray, channels: list[str]) -> dict:
    """
    Extract all features for physiological state classification.
    
    Parameters
    ----------
    data : np.ndarray
        2D array of shape (n_samples, n_channels).
    channels : list[str]
        List of channel names.
    
    Returns
    -------
    dict
        Dictionary containing all extracted features.
    """
    # Per-channel features
    channel_means = compute_channel_mean(data)
    channel_stds = compute_channel_std(data)
    channel_slopes = compute_channel_slope(data)
    channel_entropies = compute_channel_entropy(data)
    channel_ranges = compute_channel_range(data)
    
    # Global features
    coherence = compute_inter_channel_coherence(data)
    global_var = compute_global_variability(data)
    occipital = compute_occipital_activation(data, channels)
    central_activation = compute_central_activation(data, channels)
    parietal_activation = compute_parietal_activation(data, channels)
    asymmetry = compute_asymmetry(data, channels)
    stability = compute_signal_stability(data)
    
    # Aggregate statistics
    features = {
        # Per-channel aggregates
        "mean_amplitude": float(np.mean(channel_means)),
        "std_amplitude": float(np.mean(channel_stds)),
        "mean_slope": float(np.mean(channel_slopes)),
        "slope_variance": float(np.var(channel_slopes)),
        "mean_entropy": float(np.mean(channel_entropies)),
        "entropy_variance": float(np.var(channel_entropies)),
        "mean_range": float(np.mean(channel_ranges)),
        
        # Global features
        "coherence": coherence,
        "global_variability": global_var,
        "occipital_power": occipital["occipital_power"],
        "occipital_ratio": occipital["occipital_ratio"],
        "central_activation": central_activation,
        "parietal_activation": parietal_activation,
        "asymmetry": asymmetry["asymmetry"],
        "asymmetry_direction": asymmetry["asymmetry_direction"],
        "stability": stability,
        
        # Per-channel details (for detailed analysis)
        "channel_means": {ch: float(channel_means[i]) for i, ch in enumerate(channels)},
        "channel_stds": {ch: float(channel_stds[i]) for i, ch in enumerate(channels)},
        "channel_entropies": {ch: float(channel_entropies[i]) for i, ch in enumerate(channels)},
    }
    
    return features

