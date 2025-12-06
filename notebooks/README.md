# Notebooks

This folder contains Jupyter notebooks for exploratory analysis and demonstrations.

## Available Notebooks

| Notebook | Description |
|----------|-------------|
| `example_analysis.ipynb` | Basic EEG analysis workflow |

## Getting Started

```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
jupyter notebook
```

## Example Usage

```python
# In a notebook cell
import sys
sys.path.insert(0, '..')

from src.loader import load_eeg_csv
from src.hls_score import compute_hls
from src.preprocess import normalize_channels

# Load data (from additional samples or primary datasets)
time, data, channels = load_eeg_csv('../data/ADDITIONAL_samples/sample_001.csv')
# Or use primary synthetic: '../data/PRIMARY_synthetic/white_noise.csv'

# Compute HLS
data_norm = normalize_channels(data)
scores = compute_hls(data_norm)

print(f"Human Legitimacy Score: {scores['hls']:.1f}/100")
```

