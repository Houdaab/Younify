# Data Description & Component Rationale

## 1. Our Data Sources

### 1.1 Real Human EEG Data

#### Source 1: Sample EEG Files (`data/real/sample_*.csv`)
```
Format: CSV
Columns: Time, C3, C4, P3, P4, PO3, PO4, O1, O2
Samples: 7,500
Sampling Rate: 256 Hz (inferred from 4ms intervals)
Duration: ~29 seconds
```

**Channel Locations (10-20 System)**:
```
         Fp1  Fp2
    F7   F3   Fz   F4   F8
    T3   C3   Cz   C4   T4    ← Central (C3, C4)
    T5   P3   Pz   P4   T6    ← Parietal (P3, P4)
         PO3  POz  PO4        ← Parieto-Occipital
         O1   Oz   O2         ← Occipital (O1, O2)
```

**Characteristics**:
- Central channels (C3, C4): Motor/sensorimotor cortex
- Parietal channels (P3, P4): Attention, spatial processing
- Parieto-Occipital (PO3, PO4): Visual-spatial integration
- Occipital (O1, O2): Visual cortex, strong alpha rhythm

---

#### Source 2: OpenNeuro Real Human EEG (`data/real/openneuro_eyes_closed.csv`)

```
Dataset: ds004504
Task: Eyes-closed resting state
Subject: sub-001
Original Format: EEGLAB .set file
Converted to: CSV

Columns: Time, Fp1, Fp2, F3, F4, C3, C4, P3, P4
Samples: 15,000
Sampling Rate: 500 Hz
Duration: 30 seconds
```

**Recording Conditions**:
- Eyes closed (promotes alpha rhythm)
- Resting state (no task)
- Healthy adult subject

---

### 1.2 Synthetic Data (`data/synthetic/`)

We generated 8 types of synthetic signals to test what our classifier detects:

| File | Generation Method | Why It's "Fake" |
|------|-------------------|-----------------|
| `synthetic_pure_noise.csv` | `np.random.randn()` | No temporal structure |
| `synthetic_sine_waves.csv` | `sin(2πft)` per channel | Too regular, single frequency |
| `synthetic_constant.csv` | `value + tiny_noise` | No variability |
| `synthetic_square_waves.csv` | `sign(sin(2πft))` | Non-biological waveform |
| `synthetic_sawtooth.csv` | `sawtooth(2πft)` | Linear ramps, sharp resets |
| `synthetic_correlated_noise.csv` | `0.95×base + 0.05×independent` | Too correlated across channels |
| `synthetic_low_freq_drift.csv` | Sum of low-freq sines | No neural frequency bands |
| `synthetic_spike_artifacts.csv` | Noise + random large spikes | Extreme outliers |

**Each synthetic file**:
- 7,500 samples
- 8 channels (same names as real data)
- 256 Hz sampling rate

---

## 2. How We Derived the HLS Components

### The Design Process

We asked: **"What makes real EEG different from fake EEG?"**

Real EEG has specific properties that synthetic signals typically lack:

```
Real Human EEG Properties:
├── Temporal Structure (not random)
├── Spectral Complexity (not too simple or chaotic)
├── Natural Variability (not constant or uniform)
├── Inter-channel Relationships (moderate correlation)
└── Frequency Band Content (δ, θ, α, β present)
```

Each HLS component targets one or more of these properties:

---

### 2.1 PBD: Physiological Baseline Deviation

**Question**: Does the signal have realistic variance patterns?

**Why It Matters**:
- Real EEG varies in amplitude over time and across channels
- Different brain regions have different activity levels
- Electrode impedances vary, creating natural differences

**What Synthetic Signals Do Wrong**:
```python
# Synthetic often has identical variance per channel
synthetic = np.random.randn(7500, 8) * 50  # Same amplitude everywhere!

# Real EEG has natural variation
# Channel C3 might have std=45μV, O1 might have std=60μV (more alpha)
```

**Our Detection**:
```python
# Check variance consistency
var_per_channel = np.var(data, axis=0)

# Real EEG: variance differs by 10-50% between channels
# Synthetic: variance often differs by <5% (too uniform)

if variance_variation < 5%:
    penalty = 0.5  # Flag as suspicious
```

---

### 2.2 NCM: Neural Complexity Measures

**Question**: Does the signal have the right amount of "randomness"?

**Why It Matters**:
- Real EEG is **not** purely random (it has structure)
- Real EEG is **not** purely periodic (it has variability)
- Real EEG has **moderate complexity** (structured chaos)

**Spectral Entropy Scale**:
```
0.0 ─────────────── 0.7 ─────────────── 1.0
│                    │                    │
Pure Sine Wave    Real EEG           White Noise
(too regular)     (just right)       (too random)
```

**What Synthetic Signals Do Wrong**:
```python
# Sine wave: entropy ≈ 0 (power concentrated at one frequency)
sine = np.sin(2 * np.pi * 10 * t)  # All power at 10 Hz

# White noise: entropy ≈ 1 (power spread uniformly)
noise = np.random.randn(n)  # Flat spectrum

# Real EEG: entropy ≈ 0.6-0.8 (peaks at certain bands, but spread)
```

**Our Detection**:
```python
# Compute spectral entropy
freqs, psd = welch(data, fs=256)
psd_norm = psd / sum(psd)
entropy = -sum(psd_norm * log(psd_norm)) / log(len(psd))

# Score based on distance from optimal (0.7)
score = 1.0 - 2 * abs(entropy - 0.7)
```

---

### 2.3 MVI: Micro-Variability Index

**Question**: Does the signal change naturally from sample to sample?

**Why It Matters**:
- Biological signals have **1/f noise** (pink noise characteristic)
- Each sample relates to the previous one, but with variation
- The "texture" of biological signals is distinct

**What We Measure**:
```python
# First derivative (how fast signal changes)
diff1 = np.diff(data)  # Velocity

# Second derivative (how fast the change changes)
diff2 = np.diff(diff1)  # Acceleration

# Ratio of first to second derivative
ratio = mean(|diff1|) / mean(|diff2|)

# Real EEG: ratio ≈ 1.5-3.0
# Pure noise: ratio ≈ 1.0 (both derivatives similar)
# Slow drift: ratio >> 3.0 (smooth signal)
```

**What Synthetic Signals Do Wrong**:
```python
# Constant signal: no micro-variability
constant = np.ones(7500) * 10 + np.random.randn(7500) * 0.01
# diff1 ≈ 0, diff2 ≈ 0 → Fails!

# Pure noise: too much variability, wrong ratio
noise = np.random.randn(7500) * 50
# ratio ≈ 1.0 → Fails!
```

---

### 2.4 TAM: Temporal Autocorrelation Measures

**Question**: Does each sample depend on previous samples?

**Why It Matters**:
- Real neural activity has **memory** (temporal correlation)
- Brain states persist for tens to hundreds of milliseconds
- Autocorrelation decays gradually (not instantly)

**Visual Explanation**:
```
Autocorrelation vs. Lag

1.0 │●
    │ ●
    │  ●
    │   ●●
    │     ●●●
    │        ●●●●●●●
0.0 │              ●●●●●●●●●●●
    └────────────────────────────
    0ms    50ms    100ms    200ms
    
    Real EEG: Gradual decay over ~100ms
    White Noise: Instant drop to 0 at lag=1
```

**What We Measure**:
```python
# Compute autocorrelation
autocorr = correlate(x, x)

# Fit exponential decay
decay_rate = fit_exponential(autocorr[:50_lags])

# Real EEG: decay_rate ≈ 0.02-0.1
# White noise: decay_rate → ∞ (instant drop)
# Sine wave: decay_rate ≈ 0 (no decay, periodic)
```

**What Synthetic Signals Do Wrong**:
```python
# Pure noise: no temporal structure
noise = np.random.randn(7500)
# autocorr[lag>0] ≈ 0 → Fails!

# Sine wave: periodic autocorrelation (never decays)
sine = np.sin(2 * np.pi * 10 * t)
# autocorr oscillates forever → Fails!
```

---

### 2.5 NSC: Neural Signal Consistency

**Question**: Do channels relate to each other correctly?

**Why It Matters**:
- EEG channels are **not independent** (volume conduction)
- Nearby electrodes share some signal (moderate correlation)
- But channels are **not identical** (different brain regions)

**Correlation Spectrum**:
```
0.0 ────── 0.3 ────── 0.6 ────── 0.9 ────── 1.0
│           │          │          │          │
Independent  Real EEG   Real EEG   Suspicious  Same Signal
Noise       (distant)  (nearby)   (artifact)  (fake)
```

**What We Also Check - Frequency Bands**:
```
Real EEG has power in physiological bands:

Delta (δ): 0.5-4 Hz   → Deep sleep, pathology
Theta (θ): 4-8 Hz     → Drowsiness, memory
Alpha (α): 8-13 Hz    → Relaxation, eyes closed
Beta (β):  13-30 Hz   → Active thinking, focus

Synthetic signals often:
- Have NO band structure (flat spectrum)
- Have ONLY one band (pure sine wave)
- Have WRONG bands (outside 0.5-30 Hz)
```

**What Synthetic Signals Do Wrong**:
```python
# Correlated noise: ALL channels nearly identical
base = np.random.randn(7500)
channels = [0.95 * base + 0.05 * np.random.randn(7500) for _ in range(8)]
# correlation ≈ 0.95 → Too high! Fails!

# Independent noise: NO correlation
channels = [np.random.randn(7500) for _ in range(8)]
# correlation ≈ 0.0 → Too low! Fails!

# Sine wave: NO frequency bands (just one frequency)
sine = np.sin(2 * np.pi * 10 * t)
# Only alpha band → Not enough bands! Fails!
```

---

## 3. Weight Selection Rationale

| Component | Weight | Why This Weight |
|-----------|--------|-----------------|
| **PBD** | 25% | Fundamental check; most synthetic signals pass without explicit variance modeling |
| **NCM** | 10% | High variability in real EEG; legitimate signals can have unusual spectra |
| **MVI** | 25% | Very discriminative; synthetic signals rarely model micro-variability correctly |
| **TAM** | 25% | Strong discriminator; temporal structure is hard to fake |
| **NSC** | 15% | Important but depends on montage; some setups have unusual correlations |

**Total**: 25 + 10 + 25 + 25 + 15 = **100%**

---

## 4. Summary: Why Each Synthetic Type Fails

| Synthetic Type | PBD | NCM | MVI | TAM | NSC | Main Failure |
|----------------|-----|-----|-----|-----|-----|--------------|
| Pure Noise | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | No temporal structure |
| Sine Waves | ✓ | ❌ | ⚠️ | ⚠️ | ❌ | Too regular (entropy=0) |
| Constant | ❌ | ⚠️ | ❌ | ⚠️ | ⚠️ | No variance |
| Square Waves | ✓ | ❌ | ❌ | ⚠️ | ❌ | Wrong spectral shape |
| Sawtooth | ✓ | ⚠️ | ❌ | ⚠️ | ❌ | Linear ramps |
| Correlated Noise | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | Too correlated |
| Low-Freq Drift | ⚠️ | ⚠️ | ❌ | ✓ | ❌ | No high frequencies |
| Spike Artifacts | ⚠️ | ⚠️ | ❌ | ⚠️ | ⚠️ | Extreme values |

**Legend**: ✓ = Pass, ⚠️ = Marginal, ❌ = Fail

---

## 5. Visual Data Comparison

### Real Human EEG (OpenNeuro)
```
Channel Fp1: ∿∿∿∿∿∿∿∿∿∿∿∿∿  (complex waveform)
Channel C3:  ∿∿∿∿∿∿∿∿∿∿∿∿∿  (slightly different)
Channel O1:  ≈≈≈≈≈≈≈≈≈≈≈≈≈  (stronger alpha rhythm)

Properties:
- Moderate inter-channel correlation (~0.5-0.7)
- Clear alpha peak in spectrum
- Natural micro-variability
- Gradual autocorrelation decay
```

### Synthetic Sine Waves
```
Channel C3:  ∼∼∼∼∼∼∼∼∼∼∼∼∼  (perfect sine)
Channel C4:  ∼∼∼∼∼∼∼∼∼∼∼∼∼  (identical pattern)
Channel P3:  ∼∼∼∼∼∼∼∼∼∼∼∼∼  (identical pattern)

Properties:
- Zero correlation (different frequencies)
- Single spectral peak
- No micro-variability
- Periodic autocorrelation
```

### Synthetic Pure Noise
```
Channel C3:  ▓░▓░░▓░▓▓░▓░░  (random)
Channel C4:  ░▓░▓▓░▓░░▓░▓▓  (unrelated)
Channel P3:  ▓▓░░▓░░▓▓░▓░░  (unrelated)

Properties:
- Zero correlation (independent)
- Flat spectrum
- High micro-variability (but wrong ratio)
- Zero autocorrelation at lag>0
```

---

*This document explains our data and methodology for neuroscience review.*

