# Younify — Human Brain Verification Platform

**A comprehensive system for verifying human brain signals, tracking brain states on a blockchain, and managing multimedia content.**

## 🎯 Overview

Younify combines three core systems:

1. **EEG Legitimacy Analysis** — Verify if EEG signals come from real human brains using the Human Legitimacy Score (HLS)
2. **Brain State Blockchain** — Immutably track brain state sequences using a blockchain stored in MongoDB
3. **Content Management** — Upload and manage videos and EEG sessions with human verification

## 📊 Performance

**100% accuracy** on validation dataset (16 samples: 9 synthetic, 7 human) with **15.5 point separation gap** between classes.

The HLS score (0-100) combines spectral analysis, entropy, channel uniqueness, and temporal structure. **Score ≥ 50 = HUMAN**.

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (for MongoDB)

### Installation

```bash
git clone https://github.com/Houdaab/Younify.git
cd Younify/eeg-legitimacy
pip install -r requirements.txt
```

### Setup MongoDB

```bash
docker-compose up -d
```

MongoDB: `mongodb://admin:secret@localhost:27017`

### Usage

```bash
# CLI: Check if EEG is human
python -m app.human_check path/to/eeg_file.csv

# Batch process
python -m app.batch_score --data-dir data/

# Interactive dashboard
streamlit run app/dashboard.py

# API server
uvicorn app.server:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## 📡 API Endpoints

### EEG Analysis
- `POST /analyze` — Analyze EEG (JSON)
- `POST /analyze/csv` — Analyze EEG (CSV upload)
- `GET /health` — Health check

### Brain State Blockchain
- `POST /chains/new` — Create new chain
- `GET /chains` — List all chains
- `GET /chain/{chain_id}` — Get chain by ID
- `POST /chain/{chain_id}/add_node` — Add brain state node
- `POST /supply_data/{user_id}` — Upload EEG, verify human, update chain

### Video Management
- `POST /upload` — Upload video
- `GET /videos` — List videos

### Example

```bash
curl -X POST "http://localhost:8000/supply_data/user123" \
  -F "file=@path/to/eeg.csv"
```

## 🔗 System Components

### EEG Legitimacy Analysis
Verifies human brain signals using 1/f spectral slope analysis, spectral entropy, channel uniqueness, and temporal structure. See [METHODOLOGY.md](METHODOLOGY.md) for details.

### Brain State Blockchain
SHA-256 hashed blockchain nodes stored in MongoDB. Each node contains brain state data, previous hash, timestamp, and hash. Chains can be verified for integrity.

### Content Management
Upload videos and EEG sessions with automatic human verification. Files stored in `app/uploaded_videos/` and `app/uploaded_brain_sessions/`.

## 📦 Data

**Primary Datasets:**
- **HBN Multi-Task** (Human): 7 subjects, 100% accuracy, OpenNeuro ds005508
- **Synthetic HBN-Format** (Non-Human): 9 signals, 100% accuracy

See [DATA_DESCRIPTION.md](DATA_DESCRIPTION.md) for details.

## 🔧 Configuration

**MongoDB** (in `app/db.py`):
```python
MONGO_URI = "mongodb://admin:secret@localhost:27017/?authSource=admin"
DB_NAME = "brain_chain_db"
COLLECTION_NAME = "brain_states"
```

**HLS Threshold** (in `src/hls_score.py`):
```python
HUMAN_THRESHOLD = 50  # Score >= 50 = HUMAN
```

## 📄 License

MIT License — See [LICENSE](LICENSE)

## 🙏 Acknowledgments

- **HBN (Healthy Brain Network)** — Child Mind Institute
- **OpenNeuro** — Open neuroimaging data platform
