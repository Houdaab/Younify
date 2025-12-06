# EEG Legitimacy Classifier

A Python-based system for analyzing EEG signals and determining their authenticity. The project computes a **Human Legitimacy Score (HLS)** to distinguish genuine human brain activity from synthetic or artificial signals.

## 🎯 Features

- **Human Legitimacy Score (HLS)**: 0-100 score indicating signal authenticity
- **Physiological State Classification**: Classify mental states (Relaxed, Focused, Drowsy, etc.)
- **Synthetic EEG Detection**: Identify fake/artificial brain signals
- **Interactive Dashboard**: Visualize and compare EEG signals
- **REST API**: FastAPI server for integration

## 📊 How It Works

The HLS combines five feature groups:

| Component | Description | Weight |
|-----------|-------------|--------|
| **PBD** | Physiological Baseline Deviation | 25% |
| **NCM** | Neural Complexity Measures | 10% |
| **MVI** | Micro-Variability Index | 25% |
| **TAM** | Temporal Autocorrelation Measures | 25% |
| **NSC** | Neural Signal Consistency | 15% |

**Threshold**: Score ≥ 70 = Human, Score < 70 = Not Human

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/eeg-legitimacy.git
cd eeg-legitimacy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.loader import load_eeg_csv
from src.preprocess import normalize_channels
from src.hls_score import compute_hls

# Load EEG data
time, data, channels = load_eeg_csv("data/sample.csv")

# Normalize
data_norm = normalize_channels(data)

# Compute Human Legitimacy Score
scores = compute_hls(data_norm, fs=256.0)

print(f"Human Legitimacy Score: {scores['hls']:.1f}/100")
print(f"Verdict: {'HUMAN' if scores['hls'] >= 70 else 'NOT HUMAN'}")
```

### Command Line Tools

```bash
# Check if EEG is human
python -m app.human_check data/sample-eeg-data.csv

# Batch process multiple files
python -m app.batch_score --data-dir data/

# Classify mental state
python -m app.classify_states --data-dir data/

# Run interactive dashboard
streamlit run app/dashboard.py

# Start REST API server
uvicorn app.server:app --reload --port 8000
```

## 📁 Project Structure

```
eeg-legitimacy/
├── src/                    # Core modules
│   ├── __init__.py        # Package exports
│   ├── loader.py          # EEG data loading (CSV, EDF)
│   ├── preprocess.py      # Signal normalization
│   ├── features.py        # Feature extraction
│   ├── hls_score.py       # Human Legitimacy Score ⭐
│   ├── state_features.py  # State classification features
│   ├── state_classifier.py # Mental state classifier
│   ├── synthetic_eeg.py   # Synthetic signal generator
│   └── model_zoo.py       # ML model templates
├── app/                    # Applications
│   ├── __init__.py
│   ├── human_check.py     # Human verification CLI ⭐
│   ├── batch_score.py     # Batch processing
│   ├── classify_states.py # State classification
│   ├── dashboard.py       # Interactive dashboard ⭐
│   └── server.py          # FastAPI REST API
├── data/                   # EEG data files
│   ├── *.csv              # Sample EEG files
│   ├── synthetic/         # Generated synthetic signals
│   └── openneuro/         # Downloaded real human EEG
├── notebooks/              # Jupyter notebooks
├── requirements.txt        # Dependencies
├── LICENSE                 # MIT License
└── README.md               # This file
```

## 📈 Data Format

### Input CSV Format

```csv
Time,C3,C4,P3,P4,PO3,PO4,O1,O2
0.000,1.23,-0.45,0.67,-0.89,1.01,-0.23,0.45,-0.67
0.004,1.25,-0.43,0.69,-0.87,1.03,-0.21,0.47,-0.65
...
```

- **Time**: Time in seconds
- **Channels**: EEG channel values (C3, C4, P3, P4, PO3, PO4, O1, O2)
- **Sampling Rate**: Typically 256 Hz

### Supported Formats

- CSV files with Time column
- EDF/BDF files (European Data Format)

## 🔬 Feature Extraction

### Per-Channel Features
- Mean amplitude
- Standard deviation
- Slope/trend
- Entropy/complexity
- Range (peak-to-peak)

### Global Features
- Inter-channel coherence
- Global variability
- Occipital activation ratio
- Hemispheric asymmetry
- Signal stability

## 🏷️ Mental State Classification

The system classifies EEG into seven states:

| State | Characteristics |
|-------|-----------------|
| **Relaxed** | High stability, low variability, balanced coherence |
| **Focused** | High parietal activation, moderate coherence |
| **Internal Thought** | High entropy, low occipital activity |
| **Drowsy** | Very high stability, decreasing trends |
| **Meditative** | Very high coherence, balanced hemispheres |
| **Overstimulated** | High variability, high entropy |
| **Visually Engaged** | High occipital activation |

## 🌐 API Reference

### Start Server

```bash
uvicorn app.server:app --reload --port 8000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/analyze` | Analyze EEG (JSON) |
| POST | `/analyze/csv` | Analyze EEG (CSV upload) |

### Example Request

```bash
curl -X POST http://localhost:8000/analyze/csv \
  -F "file=@data/sample.csv" \
  -F "sampling_frequency=256"
```

## 🧪 Testing with Synthetic Data

Generate synthetic signals to test the classifier:

```bash
python -m src.synthetic_eeg
```

This creates 8 types of synthetic signals:
- Pure noise
- Sine waves
- Constant signal
- Square/Sawtooth waves
- Correlated noise
- Low-frequency drift
- Spike artifacts

All synthetic signals should score **below 70** (NOT HUMAN).

## 📊 Results

### Validation Results

| Data Type | HLS Score | Classification |
|-----------|-----------|----------------|
| Real Human EEG (OpenNeuro) | 74.9 | ✅ HUMAN |
| Sample EEG Data | 74.8 | ✅ HUMAN |
| Synthetic Pure Noise | 62.6 | ❌ NOT HUMAN |
| Synthetic Sine Waves | 48.2 | ❌ NOT HUMAN |

## 🔗 Data Sources

- **OpenNeuro**: [openneuro.org](https://openneuro.org/) - Free neuroimaging data
- **PhysioNet**: [physionet.org](https://physionet.org/) - Physiological signal archives

## 📦 Dependencies

- numpy >= 1.24.0
- pandas >= 2.0.0
- scipy >= 1.10.0
- fastapi >= 0.104.0
- streamlit >= 1.28.0
- plotly >= 5.18.0
- mne >= 1.5.0 (for EDF support)

## 📄 License

MIT License - See [LICENSE](LICENSE) file.

## 👥 Authors

- Your Name

## 🙏 Acknowledgments

- OpenNeuro for providing open EEG datasets
- MNE-Python for EEG processing tools
