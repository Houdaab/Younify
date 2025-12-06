# EEG Legitimacy Scoring Methodology

## Executive Summary

This document describes the methodology for computing a **Human Legitimacy Score (HLS)** that distinguishes genuine human EEG signals from synthetic/artificial signals. The primary discriminator is the **1/f spectral slope**, which is characteristic of biological neural activity.

---

## 1. Problem Statement

**Goal**: Determine whether an EEG signal originates from a genuine human brain or is artificially generated.

**Use Cases**:
- Detecting synthetic EEG in research datasets
- Validating BCI (Brain-Computer Interface) input authenticity
- Quality control for EEG recordings

---

## 2. Key Discovery: 1/f Spectral Slope

### The Discriminator

Real human EEG follows a characteristic **1/f power law** (also called "pink noise"):

```
Power ∝ 1/f^β  where β ≈ 1-2.5
```

This means when you plot log(power) vs log(frequency), you get a straight line with slope between **-1 and -2.5**.

### Why This Works

| Signal Type | Spectral Slope | Reason |
|-------------|----------------|--------|
| **Real Human EEG** | -1.0 to -2.5 | Neural activity follows power law |
| White noise | ~0 (flat) | Equal power at all frequencies |
| Synthetic sines | << -3 (very steep) | Power concentrated at specific frequencies |
| Correlated noise | ~0 (flat) | No natural frequency structure |

### Validation Results

```
SYNTHETIC DATA (spectral slopes):
  white_noise:              slope =  0.03  → NOT HUMAN ✓
  chirp:                    slope =  0.03  → NOT HUMAN ✓
  constant:                 slope = -0.08  → NOT HUMAN ✓
  correlated_99:            slope = -0.03  → NOT HUMAN ✓
  high_freq_only:           slope =  0.02  → NOT HUMAN ✓
  identical_channels:       slope =  0.03  → NOT HUMAN ✓
  linear_drift:             slope =  0.03  → NOT HUMAN ✓
  mirrored_signal:          slope = -0.03  → NOT HUMAN ✓
  pink_identical_channels:  slope = -6.19  → NOT HUMAN ✓

HBN DATA (spectral slopes):
  sub-NDARAD232HVV:         slope = -1.63  → HUMAN ✓
  sub-NDARAG584XLU:         slope = -2.06  → HUMAN ✓
  sub-NDARAH503YG1:         slope = -1.77  → HUMAN ✓
  sub-NDARAX272ZJL:         slope = -1.15  → HUMAN ✓
  sub-NDARAX283MAK:         slope = -2.30  → HUMAN ✓
  sub-NDARAX887JRN:         slope = -2.09  → HUMAN ✓
  sub-NDARAY461TZZ:         slope = -1.71  → HUMAN ✓
```

---

## 3. Human Legitimacy Score (HLS) Components

The HLS combines **four feature groups**:

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| **1/f Spectral Slope** | 40% | Power law characteristic (PRIMARY) |
| **Spectral Entropy** | 25% | Signal complexity |
| **Channel Uniqueness** | 20% | Inter-channel relationships |
| **Temporal Structure** | 15% | Autocorrelation patterns |

**Final Score**: `HLS = (0.40×Slope + 0.25×Entropy + 0.20×NSC + 0.15×TAM) × 100`

**Threshold**: HLS ≥ 50 → Human, HLS < 50 → Not Human

---

## 4. Component Details

### 4.1 Spectral Slope (40%)

**Purpose**: Detect the characteristic 1/f power law of neural activity.

**Computation**:
```python
# Compute power spectral density
freqs, psd = welch(data, fs=fs, nperseg=512)

# Fit line in log-log space (1-30 Hz range)
mask = (freqs >= 1) & (freqs <= 30)
log_f = log10(freqs[mask])
log_p = log10(psd[mask])
slope = polyfit(log_f, log_p, 1)[0]

# Score based on slope value
if -2.5 <= slope <= -0.8:
    score = 1.0  # Optimal range
elif -3.5 <= slope < -2.5:
    score = 0.7  # Slightly steep
elif slope > 0.3:
    score = 0.1  # Positive slope (wrong)
else:
    score = 0.3  # Too steep (synthetic sines)
```

**Neuroscience Basis**: 
- Neural activity generates "pink noise" (1/f)
- This arises from the hierarchical organization of brain networks
- Scale-free dynamics are a universal property of neural systems

---

### 4.2 Spectral Entropy (25%)

**Purpose**: Assess spectral complexity.

**Computation**:
```python
# Normalize PSD
psd_norm = psd / sum(psd)

# Compute entropy
entropy = -sum(psd_norm * log(psd_norm)) / log(len(psd))

# Score (optimal: 0.3-0.75)
if 0.3 <= entropy <= 0.75:
    score = 1.0
elif entropy < 0.2:
    score = entropy * 3  # Too simple
elif entropy > 0.9:
    score = (1 - entropy) * 5  # Too random
else:
    score = 0.7
```

**Neuroscience Basis**: 
- Real EEG has moderate complexity
- Pure sine waves → entropy ≈ 0 (too regular)
- White noise → entropy ≈ 1 (too random)
- Real EEG → entropy ≈ 0.4-0.7 (structured but complex)

---

### 4.3 Channel Uniqueness (20%)

**Purpose**: Check that channels are related but not identical.

**Computation**:
```python
# Compute correlations between channel pairs
correlations = []
for i in range(n_channels):
    for j in range(i+1, n_channels):
        corr = corrcoef(data[:, i], data[:, j])[0, 1]
        correlations.append(abs(corr))

max_corr = max(correlations)
mean_corr = mean(correlations)

# Score
if max_corr > 0.99:
    score = 0.05  # Identical channels (synthetic)
elif max_corr > 0.95:
    score = 0.2
elif mean_corr > 0.9:
    score = 0.3   # Too correlated
elif mean_corr < 0.05:
    score = 0.4   # Too independent
else:
    score = 0.5 + (1 - mean_corr) * 0.5
```

**Neuroscience Basis**:
- Real EEG channels share some signal (volume conduction)
- But different brain regions produce different patterns
- Typical correlation: 0.2-0.7 depending on electrode distance

---

### 4.4 Temporal Structure (15%)

**Purpose**: Verify natural autocorrelation patterns.

**Computation**:
```python
# Autocorrelation at lag 1
ac1 = corrcoef(x[:-1], x[1:])[0, 1]

# Score
if 0.3 < abs(ac1) < 0.95:
    score = 1.0  # Good temporal structure
elif abs(ac1) < 0.1:
    score = 0.3  # Too random (white noise)
elif abs(ac1) > 0.98:
    score = 0.4  # Too constant
else:
    score = 0.7
```

**Neuroscience Basis**:
- Neural activity has temporal persistence
- Brain states change gradually, not instantly
- White noise has no temporal structure

---

## 5. Validation Results

### 5.1 Classification Performance

| Data Type | N | Accuracy | HLS Range |
|-----------|---|----------|-----------|
| Synthetic Signals | 9 | 100% | 11.0 - 49.4 |
| HBN Human EEG | 7 | 100% | 64.9 - 77.2 |
| **Total** | 16 | **100%** | |

### 5.2 Separation

```
                                    THRESHOLD (50)
                                         ↓
Synthetic: ████████████████████░░░░░░░░░░│░░░░░░░░░░░░░░░░░░░░  11-49
                                         │
HBN Human: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│██████████████████████  65-77
                                         │
           0        25        50         │         75        100
                                         │
                              GAP: 15.5 points
```

---

## 6. Why Each Synthetic Type Fails

| Synthetic Type | Slope | Entropy | NSC | TAM | Main Failure |
|----------------|-------|---------|-----|-----|--------------|
| white_noise | 0.03 | 0.01 | 0.40 | 0.30 | No 1/f slope |
| chirp | 0.13 | 1.00 | 0.20 | 0.50 | No 1/f slope |
| constant | 0.14 | 0.01 | 0.40 | 0.30 | No 1/f slope |
| correlated_99 | 0.15 | 0.01 | 0.05 | 0.30 | Identical channels |
| high_freq_only | 0.14 | 0.57 | 0.20 | 0.40 | No 1/f slope |
| identical_channels | 0.13 | 0.01 | 0.05 | 0.30 | Identical channels |
| linear_drift | 0.14 | 0.01 | 0.55 | 1.00 | No 1/f slope |
| mirrored_signal | 0.15 | 0.02 | 0.05 | 0.30 | Identical channels |
| pink_identical_channels | 0.10 | 0.31 | 0.05 | 0.40 | Identical channels |

---

## 7. Limitations & Considerations

### 7.1 Known Limitations

1. **Pathological EEG**: Patients with brain injuries may have atypical spectral slopes

2. **State Dependence**: Sleep and anesthesia can alter the 1/f slope

3. **Sophisticated Fakes**: Synthetic signals designed to mimic 1/f characteristics could potentially pass

4. **Artifacts**: Heavy artifact contamination may affect the spectral slope

### 7.2 Robustness

The multi-component approach provides robustness:
- If synthetic data mimics 1/f slope, channel uniqueness can catch identical channels
- If channels are varied, spectral entropy can catch non-biological patterns
- Temporal structure provides additional validation

---

## 8. Code Location

| Component | File | Function |
|-----------|------|----------|
| Spectral Slope | `src/hls_score.py` | `compute_slope_score()` |
| Spectral Entropy | `src/hls_score.py` | `compute_spectral_entropy_score()` |
| Channel Uniqueness | `src/hls_score.py` | `compute_channel_uniqueness()` |
| Temporal Structure | `src/hls_score.py` | `compute_temporal_structure()` |
| Combined HLS | `src/hls_score.py` | `compute_hls()` |

---

## 9. References

1. He, B. J. (2014). Scale-free brain activity: past, present, and future. *Trends in Cognitive Sciences*.

2. Miller, K. J., et al. (2009). Power-law scaling in the brain surface electric potential. *PLoS Computational Biology*.

3. Voytek, B., et al. (2015). Age-related changes in 1/f neural electrophysiological noise. *Journal of Neuroscience*.

4. Donoghue, T., et al. (2020). Parameterizing neural power spectra into periodic and aperiodic components. *Nature Neuroscience*.

---

*Document Version: 2.0*  
*Last Updated: December 2024*
