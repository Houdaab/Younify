# EEG Legitimacy Scoring Methodology

## Executive Summary

This document describes the methodology for computing a **Human Legitimacy Score (HLS)** that distinguishes genuine human EEG signals from synthetic/artificial signals. The system analyzes temporal, spectral, and cross-channel characteristics to determine signal authenticity.

---

## 1. Problem Statement

**Goal**: Determine whether an EEG signal originates from a genuine human brain or is artificially generated.

**Use Cases**:
- Detecting synthetic EEG in research datasets
- Validating BCI (Brain-Computer Interface) input authenticity
- Quality control for EEG recordings

---

## 2. Data Pipeline

### 2.1 Input Format

```
CSV Format:
- Column 1: Time (seconds)
- Columns 2-N: EEG channels (e.g., C3, C4, P3, P4, PO3, PO4, O1, O2)

Sampling Rate: Typically 256 Hz (configurable)
```

### 2.2 Preprocessing

**Normalization**: Z-score normalization per channel

```python
normalized = (data - mean) / std
```

**Rationale**: Removes amplitude scaling differences between recordings while preserving relative signal characteristics.

---

## 3. Human Legitimacy Score (HLS) Components

The HLS combines **five feature groups**, each targeting different aspects of genuine EEG:

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| **PBD** | 25% | Physiological Baseline Deviation |
| **NCM** | 10% | Neural Complexity Measures |
| **MVI** | 25% | Micro-Variability Index |
| **TAM** | 25% | Temporal Autocorrelation Measures |
| **NSC** | 15% | Neural Signal Consistency |

**Final Score**: `HLS = (0.25×PBD + 0.10×NCM + 0.25×MVI + 0.25×TAM + 0.15×NSC) × 100`

**Threshold**: HLS ≥ 70 → Human, HLS < 70 → Not Human

---

## 4. Component Details

### 4.1 PBD: Physiological Baseline Deviation (25%)

**Purpose**: Verify signal conforms to expected physiological variance patterns.

**Computation**:
1. Calculate variance per channel: `var_ch = var(data[:, ch])`
2. Check variance consistency across channels
3. Compute coefficient of variation (CV)

**Scoring Logic**:
```python
# Penalize near-constant signals (synthetic often lacks variance)
if mean_variance < 0.5:
    return 0.2

# Score variance consistency (real EEG has natural inter-channel variation)
var_consistency = 1.0 - std(variance) / mean(variance)

# Penalize TOO uniform variance (synthetic often identical across channels)
if variance_ratio < 0.05:
    var_consistency *= 0.5

# CV score - optimal around 1.0
cv = std(data) / mean(abs(data))
cv_score = exp(-0.5 * (cv - 1.0)²)

PBD = (var_consistency + cv_score) / 2
```

**Neuroscience Basis**: Real EEG has natural variance differences between electrode locations due to:
- Different cortical activity at each site
- Varying impedances
- Anatomical differences

---

### 4.2 NCM: Neural Complexity Measures (10%)

**Purpose**: Assess spectral complexity typical of neural activity.

**Computation**: Spectral entropy using Welch's method

```python
for each channel:
    freqs, psd = welch(data[:, ch], fs=fs, nperseg=256)
    psd_normalized = psd / sum(psd)
    spectral_entropy = -sum(psd_norm * log(psd_norm)) / log(len(psd))
    
    # Optimal spectral entropy for EEG: 0.6-0.8
    score = 1.0 - 2 * |spectral_entropy - 0.7|

NCM = mean(scores)
```

**Neuroscience Basis**: 
- Real EEG has **moderate** spectral entropy (not too regular, not random)
- Pure sine waves → entropy ≈ 0 (too regular)
- White noise → entropy ≈ 1 (too random)
- Real EEG → entropy ≈ 0.6-0.8 (structured but complex)

**Weight Justification**: Lower weight (10%) because:
- Spectral characteristics vary widely across states and individuals
- Some legitimate EEG can have atypical spectral profiles

---

### 4.3 MVI: Micro-Variability Index (25%)

**Purpose**: Detect natural sample-to-sample variations characteristic of biological signals.

**Computation**:
```python
# First-order differences (velocity)
diff1 = diff(data, axis=0)
micro_var = mean(abs(diff1))

# Second-order differences (acceleration)
diff2 = diff(diff1, axis=0)
micro_var2 = mean(abs(diff2))

# Ratio of first to second order
ratio = micro_var / micro_var2

# Optimal ratio for biological signals: 1.5-3.0
ratio_score = exp(-0.3 * (ratio - 2.0)²)

# Zero-crossing rate in differences
zc_rate = count(sign_changes) / n_samples

# Real EEG has ~50% zero-crossing rate with variation across channels
if zc_std < 0.01:  # Too uniform = synthetic
    zc_score = 0.3
else:
    zc_score = clip(zc_rate / 0.5, 0, 1)

MVI = (ratio_score + zc_score) / 2
```

**Neuroscience Basis**:
- Biological signals have characteristic **1/f noise** (pink noise)
- Synthetic signals often lack natural micro-fluctuations
- The ratio of first to second derivatives distinguishes signal types

---

### 4.4 TAM: Temporal Autocorrelation Measures (25%)

**Purpose**: Verify temporal structure expected from neural dynamics.

**Computation**:
```python
for each channel:
    x = data[:, ch] - mean(data[:, ch])
    
    # Autocorrelation
    autocorr = correlate(x, x, mode='full')
    autocorr = autocorr / autocorr[0]  # Normalize
    
    # Measure decay rate
    decay_rate = -polyfit(range(max_lag), log(abs(autocorr[:max_lag])), 1)[0]
    
    # Optimal decay rate for EEG: 0.02-0.1
    score = exp(-5 * (decay_rate - 0.05)²)

TAM = mean(scores)
```

**Neuroscience Basis**:
- Real EEG has **temporal structure** - each sample depends on previous samples
- Autocorrelation decays gradually (not instantly like white noise)
- Decay rate reflects neural time constants

---

### 4.5 NSC: Neural Signal Consistency (15%)

**Purpose**: Check cross-channel relationships and frequency band presence.

**Computation**:

```python
# Part 1: Inter-channel correlation
corr_matrix = corrcoef(data.T)
mean_corr = mean(abs(upper_triangle))

# Scoring:
if mean_corr > 0.95:      # Too correlated = synthetic
    corr_score = 0.1
elif mean_corr < 0.05:    # Uncorrelated = independent noise
    corr_score = 0.3
else:
    # Real EEG: moderate correlation (0.2-0.8)
    corr_score = 1.0 - 1.5 * |mean_corr - 0.5|

# Part 2: Frequency band presence
for each channel:
    freqs, psd = welch(data[:, ch], fs=fs)
    
    # Check standard EEG bands
    delta_power = sum(psd[0.5-4 Hz]) / total_power
    theta_power = sum(psd[4-8 Hz]) / total_power
    alpha_power = sum(psd[8-13 Hz]) / total_power
    beta_power  = sum(psd[13-30 Hz]) / total_power
    
    # Each band should have 5-40% of power
    bands_present = count(bands with 0.05 < power < 0.4)
    band_score = bands_present / 4

NSC = (corr_score + band_score) / 2
```

**Neuroscience Basis**:
- Real EEG channels are **moderately correlated** due to volume conduction
- Too high correlation (>0.95) suggests common noise source
- Too low correlation (<0.05) suggests independent noise
- Real EEG contains power in standard frequency bands (δ, θ, α, β)

---

## 5. Validation Data

### 5.1 Real Human EEG

**Source**: OpenNeuro dataset ds004504
- Task: Eyes-closed resting state
- Channels: 19 (Fp1, Fp2, F3, F4, C3, C4, P3, P4, O1, O2, etc.)
- Sampling rate: 500 Hz
- Duration: ~10 minutes

**Expected Result**: HLS ≥ 70 (HUMAN)

### 5.2 Synthetic Signals (Controls)

| Signal Type | Generation Method | Expected HLS | Reason for Failure |
|-------------|-------------------|--------------|-------------------|
| Pure Noise | `randn(n, ch)` | ~62 | No temporal structure (TAM) |
| Sine Waves | `sin(2πft)` | ~48 | No complexity (NCM=0) |
| Constant | `value + tiny_noise` | ~62 | No variance (PBD, MVI) |
| Square Waves | `sign(sin(2πft))` | ~58 | Non-biological shape (NCM) |
| Sawtooth | `sawtooth(2πft)` | ~61 | Wrong spectral content |
| Correlated Noise | `0.95*base + 0.05*indep` | ~61 | Too high correlation (NSC) |
| Low-Freq Drift | `sum(sin(low_freqs))` | ~62 | No high-frequency content |
| Spike Artifacts | `noise + random_spikes` | ~55 | Extreme outliers (MVI) |

---

## 6. Results Summary

### 6.1 Classification Performance

| Data Type | N | Mean HLS | Classification |
|-----------|---|----------|----------------|
| Real Human EEG | 4 | 74.5 | ✅ HUMAN (100%) |
| Synthetic Signals | 8 | 58.5 | ❌ NOT HUMAN (100%) |

### 6.2 Score Distribution

```
Real Human EEG:    ████████████████████████████████████░░░░  74-75
                                                        ↑
                                              Threshold (70)
                                                        ↓
Synthetic Signals: ████████████████████████░░░░░░░░░░░░░░░░  48-62
```

---

## 7. Limitations & Considerations

### 7.1 Known Limitations

1. **Sampling Rate Sensitivity**: Some features depend on sampling rate; fs should be consistent or normalized

2. **Electrode Montage**: Current validation uses 8-19 channel montages; performance with fewer channels not validated

3. **Pathological EEG**: Patients with epilepsy, brain injuries, etc. may have atypical patterns

4. **State Dependence**: Sleep, anesthesia, and coma may produce different spectral profiles

5. **Artifacts**: Heavy artifact contamination (EMG, EOG, line noise) may affect scores

### 7.2 Recommendations for Reviewers

**Questions to Consider**:

1. Are the frequency band definitions (δ, θ, α, β) appropriate for the use case?

2. Is the inter-channel correlation range (0.2-0.8) reasonable for various montages?

3. Should the NCM weight be higher for applications requiring spectral validation?

4. Are there additional features that would improve discrimination?

5. Should the threshold (70) be adjusted based on the specific application?

---

## 8. Component Weight Rationale

| Component | Weight | Rationale |
|-----------|--------|-----------|
| **PBD** | 25% | Fundamental physiological check |
| **NCM** | 10% | High individual variability |
| **MVI** | 25% | Strong discriminator for synthetic |
| **TAM** | 25% | Captures temporal dynamics |
| **NSC** | 15% | Cross-channel validation |

**Note**: Weights can be adjusted via the `weights` parameter in `compute_hls()`.

---

## 9. References

1. Welch, P. D. (1967). The use of fast Fourier transform for the estimation of power spectra.

2. Higuchi, T. (1988). Approach to an irregular time series on the basis of the fractal theory.

3. Stam, C. J. (2005). Nonlinear dynamical analysis of EEG and MEG: Review of an emerging field.

4. Delorme, A., & Makeig, S. (2004). EEGLAB: an open source toolbox for analysis of single-trial EEG dynamics.

---

## 10. Code Location

| Component | File | Function |
|-----------|------|----------|
| PBD | `src/hls_score.py` | `compute_pbd()` |
| NCM | `src/hls_score.py` | `compute_ncm()` |
| MVI | `src/hls_score.py` | `compute_mvi()` |
| TAM | `src/hls_score.py` | `compute_tam()` |
| NSC | `src/hls_score.py` | `compute_nsc()` |
| Combined HLS | `src/hls_score.py` | `compute_hls()` |

---

*Document Version: 1.0*
*Last Updated: December 2024*

