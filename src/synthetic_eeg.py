"""
Synthetic EEG Generator

Generates various types of non-human/fake EEG signals for testing the HLS classifier.

Types of synthetic signals:
1. Pure noise (random) - no temporal structure
2. Sine waves - too regular, no complexity
3. Filtered noise - lacks biological frequency bands
4. Constant signal - no variability
5. Sawtooth/square waves - non-biological patterns
6. Correlated noise - wrong correlation structure
"""

import numpy as np
from scipy import signal
import pandas as pd
from pathlib import Path


def generate_pure_noise(
    n_samples: int = 7500,
    n_channels: int = 8,
    amplitude: float = 50.0,
    seed: int | None = None
) -> np.ndarray:
    """
    Generate pure random noise (white noise).
    
    Should fail HLS because:
    - No temporal autocorrelation (TAM will be low)
    - Flat spectrum (NCM will be wrong)
    - No physiological frequency bands (NSC will be low)
    """
    if seed is not None:
        np.random.seed(seed)
    return np.random.randn(n_samples, n_channels) * amplitude


def generate_sine_waves(
    n_samples: int = 7500,
    n_channels: int = 8,
    frequencies: list[float] | None = None,
    amplitude: float = 50.0,
    fs: float = 256.0,
    seed: int | None = None
) -> np.ndarray:
    """
    Generate pure sine waves (too regular).
    
    Should fail HLS because:
    - Too regular/predictable (very low entropy)
    - No natural variability (MVI will be wrong)
    - Single frequency per channel (NCM will be very low)
    """
    if seed is not None:
        np.random.seed(seed)
    
    if frequencies is None:
        frequencies = [5, 7, 10, 12, 8, 6, 11, 9]  # Hz
    
    t = np.arange(n_samples) / fs
    data = np.zeros((n_samples, n_channels))
    
    for ch in range(n_channels):
        freq = frequencies[ch % len(frequencies)]
        phase = np.random.uniform(0, 2 * np.pi)
        data[:, ch] = amplitude * np.sin(2 * np.pi * freq * t + phase)
    
    return data


def generate_constant_signal(
    n_samples: int = 7500,
    n_channels: int = 8,
    values: list[float] | None = None,
    noise_level: float = 0.1
) -> np.ndarray:
    """
    Generate near-constant signal with minimal variation.
    
    Should fail HLS because:
    - No variability (PBD, MVI will be very low)
    - No temporal structure
    - No frequency content
    """
    if values is None:
        values = [10, -5, 15, -10, 8, -3, 12, -8]
    
    data = np.zeros((n_samples, n_channels))
    for ch in range(n_channels):
        base = values[ch % len(values)]
        data[:, ch] = base + np.random.randn(n_samples) * noise_level
    
    return data


def generate_square_waves(
    n_samples: int = 7500,
    n_channels: int = 8,
    frequencies: list[float] | None = None,
    amplitude: float = 50.0,
    fs: float = 256.0
) -> np.ndarray:
    """
    Generate square waves (non-biological pattern).
    
    Should fail HLS because:
    - Non-biological waveform shape
    - Abrupt transitions (wrong MVI pattern)
    - Harmonic-rich spectrum (wrong NCM)
    """
    if frequencies is None:
        frequencies = [2, 3, 2.5, 1.5, 2, 3, 2.5, 1.5]  # Hz
    
    t = np.arange(n_samples) / fs
    data = np.zeros((n_samples, n_channels))
    
    for ch in range(n_channels):
        freq = frequencies[ch % len(frequencies)]
        data[:, ch] = amplitude * signal.square(2 * np.pi * freq * t)
    
    return data


def generate_sawtooth_waves(
    n_samples: int = 7500,
    n_channels: int = 8,
    frequencies: list[float] | None = None,
    amplitude: float = 50.0,
    fs: float = 256.0
) -> np.ndarray:
    """
    Generate sawtooth waves (non-biological pattern).
    
    Should fail HLS because:
    - Linear ramps are not biological
    - Abrupt resets
    - Wrong spectral content
    """
    if frequencies is None:
        frequencies = [1, 1.5, 2, 1.2, 1, 1.5, 2, 1.2]  # Hz
    
    t = np.arange(n_samples) / fs
    data = np.zeros((n_samples, n_channels))
    
    for ch in range(n_channels):
        freq = frequencies[ch % len(frequencies)]
        data[:, ch] = amplitude * signal.sawtooth(2 * np.pi * freq * t)
    
    return data


def generate_correlated_noise(
    n_samples: int = 7500,
    n_channels: int = 8,
    correlation: float = 0.95,
    amplitude: float = 50.0,
    seed: int | None = None
) -> np.ndarray:
    """
    Generate highly correlated noise across channels.
    
    Should fail HLS because:
    - Too high inter-channel correlation (NSC will flag this)
    - Real EEG has moderate, not extreme correlation
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate base signal
    base = np.random.randn(n_samples) * amplitude
    
    # Add correlated noise to each channel
    data = np.zeros((n_samples, n_channels))
    for ch in range(n_channels):
        independent = np.random.randn(n_samples) * amplitude
        data[:, ch] = correlation * base + (1 - correlation) * independent
    
    return data


def generate_low_frequency_drift(
    n_samples: int = 7500,
    n_channels: int = 8,
    amplitude: float = 100.0,
    fs: float = 256.0,
    seed: int | None = None
) -> np.ndarray:
    """
    Generate slow drifting signal (electrode drift artifact).
    
    Should fail HLS because:
    - No high-frequency content
    - Too smooth/stable
    - Wrong spectral distribution
    """
    if seed is not None:
        np.random.seed(seed)
    
    t = np.arange(n_samples) / fs
    data = np.zeros((n_samples, n_channels))
    
    for ch in range(n_channels):
        # Very low frequency components
        drift = amplitude * (
            0.5 * np.sin(2 * np.pi * 0.05 * t + np.random.uniform(0, 2*np.pi)) +
            0.3 * np.sin(2 * np.pi * 0.1 * t + np.random.uniform(0, 2*np.pi)) +
            0.2 * np.sin(2 * np.pi * 0.02 * t + np.random.uniform(0, 2*np.pi))
        )
        data[:, ch] = drift + np.random.randn(n_samples) * 2  # Small noise
    
    return data


def generate_spike_artifacts(
    n_samples: int = 7500,
    n_channels: int = 8,
    spike_rate: float = 0.01,
    amplitude: float = 200.0,
    seed: int | None = None
) -> np.ndarray:
    """
    Generate signal with random spikes (artifact-like).
    
    Should fail HLS because:
    - Extreme amplitude outliers
    - Non-biological spike pattern
    - Wrong variability structure
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Base noise
    data = np.random.randn(n_samples, n_channels) * 10
    
    # Add random spikes
    n_spikes = int(n_samples * spike_rate)
    for ch in range(n_channels):
        spike_indices = np.random.choice(n_samples, n_spikes, replace=False)
        spike_values = np.random.choice([-1, 1], n_spikes) * amplitude
        data[spike_indices, ch] += spike_values
    
    return data


def generate_synthetic_dataset(
    output_dir: str = "data/synthetic",
    n_samples: int = 7500,
    fs: float = 256.0,
    channels: list[str] | None = None
) -> list[Path]:
    """
    Generate a complete dataset of synthetic EEG signals for testing.
    
    Creates multiple CSV files with different types of fake signals.
    
    Parameters
    ----------
    output_dir : str
        Directory to save synthetic files.
    n_samples : int
        Number of samples per file.
    fs : float
        Sampling frequency.
    channels : list[str]
        Channel names.
    
    Returns
    -------
    list[Path]
        List of created file paths.
    """
    if channels is None:
        channels = ["C3", "C4", "P3", "P4", "PO3", "PO4", "O1", "O2"]
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Time array
    time = np.arange(n_samples) / fs
    
    # Define generators
    generators = {
        "pure_noise": lambda: generate_pure_noise(n_samples, len(channels), seed=42),
        "sine_waves": lambda: generate_sine_waves(n_samples, len(channels), fs=fs, seed=42),
        "constant": lambda: generate_constant_signal(n_samples, len(channels)),
        "square_waves": lambda: generate_square_waves(n_samples, len(channels), fs=fs),
        "sawtooth": lambda: generate_sawtooth_waves(n_samples, len(channels), fs=fs),
        "correlated_noise": lambda: generate_correlated_noise(n_samples, len(channels), seed=42),
        "low_freq_drift": lambda: generate_low_frequency_drift(n_samples, len(channels), fs=fs, seed=42),
        "spike_artifacts": lambda: generate_spike_artifacts(n_samples, len(channels), seed=42),
    }
    
    created_files = []
    
    for name, generator in generators.items():
        data = generator()
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=channels)
        df.insert(0, "Time", time)
        
        # Save to CSV
        filepath = output_path / f"synthetic_{name}.csv"
        df.to_csv(filepath, index=False)
        created_files.append(filepath)
        print(f"Created: {filepath}")
    
    return created_files


if __name__ == "__main__":
    print("Generating synthetic EEG dataset...")
    files = generate_synthetic_dataset()
    print(f"\nGenerated {len(files)} synthetic EEG files in data/synthetic/")

