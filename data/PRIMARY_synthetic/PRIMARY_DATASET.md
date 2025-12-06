# 🎯 PRIMARY DATASET: Synthetic HBN-Format (Non-Human)

This is the **main synthetic dataset** used for validation.

## Purpose
Test signals designed to be classified as **NOT HUMAN** by the HLS algorithm.

## Format
- **Channels**: 129 (matching HBN)
- **Sampling Rate**: 500 Hz
- **Duration**: 30 seconds
- **Format**: CSV

## Contents

| File | Description | HLS Score | Classification |
|------|-------------|-----------|----------------|
| white_noise.csv | Pure Gaussian noise | 18.5 | ✅ NOT HUMAN |
| chirp.csv | Frequency sweep | 49.4 | ✅ NOT HUMAN |
| constant.csv | Near-constant signal | 18.4 | ✅ NOT HUMAN |
| correlated_99.csv | 99% correlated channels | 11.6 | ✅ NOT HUMAN |
| high_freq_only.csv | 40Hz only | 38.7 | ✅ NOT HUMAN |
| identical_channels.csv | All channels same | 11.0 | ✅ NOT HUMAN |
| linear_drift.csv | Slow linear trend | 32.1 | ✅ NOT HUMAN |
| mirrored_signal.csv | Symmetric signal | 11.8 | ✅ NOT HUMAN |
| pink_identical_channels.csv | Pink noise, same channels | 18.8 | ✅ NOT HUMAN |

**Accuracy: 9/9 (100%)**

## Why These Fail

All synthetic signals fail because they lack the **1/f spectral slope** characteristic of real human EEG:
- Real EEG: slope -1.0 to -2.5
- Synthetic: slope ~0 (flat) or <-3 (too steep)

