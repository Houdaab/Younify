# Younify — Human Brain Verification Platform

**A comprehensive system for verifying human brain signals, tracking brain states on a blockchain, and managing multimedia content.**

## 🎯 What This Does

Younify combines three core systems:

1. **EEG Legitimacy Analysis** — Verify if EEG signals come from real human brains using the Human Legitimacy Score (HLS)
2. **Brain State Blockchain** — Immutably track brain state sequences using a blockchain stored in MongoDB
3. **Content Management** — Upload and manage videos and EEG sessions with human verification

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server (app/server.py)           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   EEG APIs   │  │  Blockchain  │  │ Video/Upload │     │
│  │              │  │     APIs     │  │     APIs     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘             │
│                            │                                 │
│  ┌─────────────────────────┴─────────────────────────┐     │
│  │         Core Analysis Modules (src/)               │     │
│  │  • HLS Scoring  • Feature Extraction              │     │
│  │  • State Classification  • Signal Processing      │     │
│  └────────────────────────────────────────────────────┘     │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         ┌──────▼──────┐          ┌──────▼──────┐
         │  MongoDB    │          │  File System │
         │  (Blockchain)│          │  (Uploads)   │
         └─────────────┘          └──────────────┘
```

## 📊 EEG Legitimacy Classification

**100% accuracy** on curated validation dataset:

| Dataset | Samples | Accuracy | HLS Range |
|---------|---------|----------|-----------|
| **Synthetic (NOT HUMAN)** | 9 | 100% | 11.0 - 49.4 |
| **HBN Human (HUMAN)** | 7 | 100% | 64.9 - 77.2 |
| **Overall** | 16 | **100%** | |

**Separation Gap**: 15.5 points between classes (no overlap)

### HLS Score Components

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

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (for MongoDB)
- pip or Poetry

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

### Setup MongoDB

```bash
# Start MongoDB using Docker Compose
docker-compose up -d

# Verify MongoDB is running
docker ps | grep mongo
```

MongoDB will be available at `mongodb://admin:secret@localhost:27017`

### Usage

#### 1. Check if an EEG file is human (CLI)

```bash
python -m app.human_check path/to/eeg_file.csv
```

#### 2. Batch process multiple files

```bash
python -m app.batch_score --data-dir data/
```

#### 3. Run the interactive dashboard

```bash
streamlit run app/dashboard.py
```

#### 4. Start the API server

```bash
uvicorn app.server:app --reload --port 8000
```

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### EEG Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze EEG data (JSON input) |
| `/analyze/csv` | POST | Analyze EEG data (CSV file upload) |
| `/health` | GET | Health check |

### Brain State Blockchain

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chains/new` | POST | Create a new brain state chain |
| `/chains` | GET | List all chain summaries |
| `/chain/{chain_id}` | GET | Get full chain by ID |
| `/chain/{chain_id}/add_node` | POST | Add a new brain state node |
| `/supply_data/{user_id}` | POST | Upload EEG, verify human, update chain |

### Video Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload video file |
| `/videos` | GET | List all uploaded videos |

### Example: Upload EEG and Verify Human

```bash
curl -X POST "http://localhost:8000/supply_data/user123" \
  -F "file=@path/to/eeg.csv"
```

Response:
```json
{
  "message": "EEG uploaded and verified",
  "user_id": "user123",
  "eeg_file": "uuid.csv",
  "is_human": true,
  "chain_id": "chain-uuid",
  "hls_score": 72.5,
  "verdict": "HUMAN"
}
```

## 📁 Project Structure

```
eeg-legitimacy/
├── src/                          # Core analysis modules
│   ├── loader.py                 # EEG file loading (CSV, EDF, SET)
│   ├── preprocess.py             # Signal normalization
│   ├── features.py               # Feature extraction
│   ├── hls_score.py              # Human Legitimacy Score (1/f slope)
│   ├── state_features.py         # State classification features
│   ├── state_classifier.py       # Mental state classification
│   ├── synthetic_eeg.py          # Synthetic signal generation
│   └── model_zoo.py              # ML model templates
│
├── app/                          # Applications & API
│   ├── server.py                 # FastAPI server (main API)
│   ├── dashboard.py              # Streamlit visualization
│   ├── human_check.py            # CLI human verification
│   ├── batch_score.py            # Batch processing
│   ├── analyze_hbn_multitask.py  # HBN dataset analysis
│   │
│   ├── blockchain.py            # Brain state blockchain logic
│   ├── db.py                     # MongoDB database operations
│   │
│   ├── models/                   # Pydantic models
│   │   ├── api.py                # API request/response models
│   │   └── internal.py           # Internal data models
│   │
│   ├── test_brain_sessions_upload/  # EEG upload tests
│   └── test_video_upload/          # Video upload tests
│
├── data/
│   ├── PRIMARY_hbn_human/        # 🎯 Main human EEG (7 subjects)
│   ├── PRIMARY_synthetic/        # 🎯 Main synthetic signals (9 files)
│   ├── ADDITIONAL_samples/       # Supporting: Sample EEG
│   └── ADDITIONAL_openneuro/     # Supporting: Extended validation
│
├── notebooks/                    # Jupyter notebooks (analysis)
│
├── docker-compose.yaml           # MongoDB setup
├── METHODOLOGY.md                # Technical methodology
├── DATA_DESCRIPTION.md           # Data documentation
├── requirements.txt              # Python dependencies
└── pyproject.toml                # Poetry configuration
```

## 🔗 System Components

### 1. EEG Legitimacy Analysis

**Purpose**: Verify if EEG signals are from real human brains

**Key Features**:
- Human Legitimacy Score (HLS) calculation
- 1/f spectral slope analysis
- Multi-feature classification
- State classification (Relaxed, Focused, Meditative, etc.)

**Files**:
- `src/hls_score.py` — Core HLS computation
- `src/features.py` — Feature extraction
- `app/human_check.py` — CLI tool
- `app/dashboard.py` — Interactive visualization

### 2. Brain State Blockchain

**Purpose**: Immutably track sequences of brain states

**Key Features**:
- SHA-256 hashed blockchain nodes
- Chain integrity verification
- MongoDB persistence
- User metadata (name, gender)

**Files**:
- `app/blockchain.py` — Blockchain logic
- `app/db.py` — MongoDB operations
- `app/models/internal.py` — Data models

**How It Works**:
1. Each brain state is a node with: `state_data`, `previous_hash`, `hash`, `timestamp`
2. Nodes are linked via `previous_hash` → `hash` chain
3. Full chain stored in MongoDB document
4. Chain can be verified for integrity

### 3. Content Management

**Purpose**: Upload and manage videos and EEG sessions

**Key Features**:
- Video file upload (MP4, MOV, AVI, etc.)
- EEG CSV upload with automatic human verification
- File storage and listing
- Integration with blockchain system

**Files**:
- `app/server.py` — Upload endpoints
- Upload directories: `app/uploaded_videos/`, `app/uploaded_brain_sessions/`

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

## 🗄️ Database Schema

### MongoDB Collection: `brain_states`

```json
{
  "_id": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  "gender": "male",
  "is_human": true,
  "nodes": [
    {
      "state_data": "0,1,1,0,1,0,0,1",
      "previous_hash": "",
      "hash": "abc123...",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "state_data": "0,1,1,1,1,0,1,0",
      "previous_hash": "abc123...",
      "hash": "def456...",
      "timestamp": "2024-01-01T00:01:00Z"
    }
  ]
}
```

## 🧪 Testing

### Test EEG Upload

```bash
python app/test_brain_sessions_upload/test_brain_session_upload.py
```

### Test Video Upload

```bash
python app/test_video_upload/test_video_upload.py
```

## 🔧 Configuration

### MongoDB Connection

Default connection string (in `app/db.py`):
```python
MONGO_URI = "mongodb://admin:secret@localhost:27017/?authSource=admin"
DB_NAME = "brain_chain_db"
COLLECTION_NAME = "brain_states"
```

### HLS Threshold

Default threshold (in `src/hls_score.py`):
```python
HUMAN_THRESHOLD = 50  # Score >= 50 = HUMAN
```

## 📄 License

MIT License — See [LICENSE](LICENSE)

## 🙏 Acknowledgments

- **HBN (Healthy Brain Network)** — Child Mind Institute
- **OpenNeuro** — Open neuroimaging data platform
- Data formatted in BIDS (Brain Imaging Data Structure)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📞 Support

For questions or issues, please open an issue on GitHub.
