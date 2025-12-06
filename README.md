# Younify EEG Legitimacy Classifier

**Human Legitimacy Score (HLS)** — A system to verify if an EEG signal comes from a real human brain.

## 🎯 What This Does

1. **Human vs Non-Human Classification** — Detect if EEG is from a real brain or synthetic/AI-generated
2. **Identity Consistency** — Verify that the same person shows stable brain signatures across different tasks
3. **State Classification** — Identify mental states (Relaxed, Focused, Meditative, etc.)

## 📊 Classification Results

**100% accuracy** on curated validation dataset:

| Dataset | Samples | Accuracy | HLS Range |
|---------|---------|----------|-----------|
| **Synthetic (NOT HUMAN)** | 9 | 100% | 11.0 - 49.4 |
| **HBN Human (HUMAN)** | 7 | 100% | 64.9 - 77.2 |
| **Overall** | 16 | **100%** | |

**Separation Gap**: 15.5 points between classes (no overlap)

## 🧠 HLS Score Components

The HLS (0-100) uses a **1/f spectral slope** as the primary discriminator:

| Component | Weight | What It Checks |
|-----------|--------|----------------|
| **1/f Spectral Slope** | 40% | Real EEG follows power law (slope -1 to -2.5) |
| **Spectral Entropy** | 25% | Moderate complexity (not too regular/random) |
| **Channel Uniqueness** | 20% | Channels correlated but not identical |
| **Temporal Structure** | 15% | Natural autocorrelation patterns |

**Score ≥ 50 = HUMAN** | **Score < 50 = NOT HUMAN**

### Why 1/f Slope Works

| Signal Type | Spectral Slope | Classification |
|-------------|----------------|----------------|
| Real human EEG | -1.0 to -2.5 | ✅ HUMAN |
| White noise | ~0 | ❌ NOT HUMAN |
| Synthetic sines | < -3 (too steep) | ❌ NOT HUMAN |
| Correlated noise | ~0 | ❌ NOT HUMAN |

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Houdaab/Younify.git
cd Younify/eeg-legitimacy

# Install dependencies
pip install -r requirements.txt

# Or with Poetry
poetry install
```

### Usage

#### 1. Check if an EEG file is human

```bash
python -m app.human_check path/to/eeg_file.csv
```

#### 2. Batch process multiple files

```bash
python -m app.batch_score --data-dir data/
```

#### 3. Run the dashboard

```bash
streamlit run app/dashboard.py
```

#### 4. Start the API server

```bash
uvicorn app.server:app --reload
```

## 📁 Project Structure

```
eeg-legitimacy/
├── src/                      # Core modules
│   ├── loader.py             # EEG file loading (CSV, EDF, SET)
│   ├── preprocess.py         # Signal normalization
│   ├── features.py           # Feature extraction
│   ├── hls_score.py          # Human Legitimacy Score (1/f slope)
│   ├── state_features.py     # State classification features
│   ├── state_classifier.py   # Mental state classification
│   └── synthetic_eeg.py      # Synthetic signal generation
│
├── app/                      # Applications
│   ├── dashboard.py          # Streamlit visualization
│   ├── human_check.py        # CLI human verification
│   ├── batch_score.py        # Batch processing
│   ├── analyze_hbn_multitask.py  # HBN dataset analysis
│   └── server.py             # FastAPI REST API
│
├── data/
│   ├── PRIMARY_hbn_human/    # 🎯 Main human EEG (7 subjects)
│   ├── PRIMARY_synthetic/    # 🎯 Main synthetic signals (9 files)
│   ├── ADDITIONAL_samples/   # Supporting: Sample EEG
│   └── ADDITIONAL_openneuro/ # Supporting: Extended validation
│
├── METHODOLOGY.md            # Technical methodology
├── DATA_DESCRIPTION.md       # Data documentation
├── requirements.txt          # Python dependencies
└── pyproject.toml            # Poetry configuration
```

## 📦 Data

### 🎯 PRIMARY DATASETS (Main Focus)

| Dataset | Type | Samples | Accuracy | Purpose |
|---------|------|---------|----------|---------|
| **HBN Multi-Task** | Human | 7 subjects | 100% HUMAN | Real brain validation |
| **Synthetic HBN-Format** | Non-Human | 9 signals | 100% NOT HUMAN | Fake detection |

```
data/
├── PRIMARY_hbn_human/       ← 🎯 Main human EEG (7 subjects)
├── PRIMARY_synthetic/       ← 🎯 Main synthetic signals (9 files)
├── ADDITIONAL_samples/      ← Supporting: Sample EEG
└── ADDITIONAL_openneuro/    ← Supporting: Extended validation
```

#### HBN Multi-Task (Human Data)
- **Source**: OpenNeuro ds005508 (Healthy Brain Network)
- **Subjects**: 7 verified humans (children/adolescents)
- **Format**: EEGLAB .set (500 Hz, 129 channels)
- **Task**: Resting State
- **Size**: ~4.6 GB (download separately)

#### Synthetic HBN-Format (Non-Human Data)
- **Purpose**: Validation controls
- **Format**: CSV (500 Hz, 129 channels, 30 seconds)
- **Size**: ~327 MB (included in repo)

### Synthetic Signal Types

| Signal | Why It's Non-Human |
|--------|-------------------|
| white_noise | No temporal structure (slope ~0) |
| chirp | Frequency sweep, non-stationary |
| constant | Near-zero variability |
| correlated_99 | Channels 99% identical |
| high_freq_only | 40Hz only (wrong spectrum) |
| identical_channels | All channels same |
| linear_drift | No oscillations |
| mirrored_signal | Perfectly symmetric |
| pink_identical_channels | Right slope but identical channels |

### 📁 Additional Data (Supporting)

These datasets are **not the main focus** but can be used for extended validation:

- **`data/ADDITIONAL_samples/`**: 4 sample human EEG files (CSV, 256 Hz)
- **`data/ADDITIONAL_openneuro/`**: 5 OpenNeuro datasets for cross-validation

## 🔬 Methodology

See [METHODOLOGY.md](METHODOLOGY.md) for detailed technical documentation.

### Key Findings

1. **1/f spectral slope is the primary discriminator**
   - Real EEG: slope -1.0 to -2.5 (characteristic pink noise)
   - Synthetic: slope ~0 (white noise) or < -3 (sine waves)

2. **Multiple features provide robustness**
   - Spectral entropy catches regularity issues
   - Channel uniqueness catches identical/correlated channels
   - Temporal structure catches non-biological dynamics

3. **Perfect separation achieved**
   - 15.5 point gap between synthetic max (49.4) and human min (64.9)

## 📄 License

MIT License — See [LICENSE](LICENSE)

## 🙏 Acknowledgments

- **HBN (Healthy Brain Network)** — Child Mind Institute
- **OpenNeuro** — Open neuroimaging data platform
- Data formatted in BIDS (Brain Imaging Data Structure)
