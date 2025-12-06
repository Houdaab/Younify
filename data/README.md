# Data Directory

## Structure

```
data/
├── PRIMARY_hbn_human/       ← 🎯 Main human EEG dataset
├── PRIMARY_synthetic/       ← 🎯 Main synthetic test signals
├── ADDITIONAL_samples/      ← Supporting sample files
└── ADDITIONAL_openneuro/    ← Supporting OpenNeuro datasets
```

---

## 🎯 PRIMARY DATASETS

These are the **main datasets** used for Human Legitimacy Score validation:

| Folder | Type | Contents | Accuracy |
|--------|------|----------|----------|
| **`PRIMARY_hbn_human/`** | Human | 7 subjects from HBN | 100% HUMAN |
| **`PRIMARY_synthetic/`** | Non-Human | 9 synthetic signals | 100% NOT HUMAN |

**Total Classification Accuracy: 16/16 (100%)**

---

## 📁 ADDITIONAL DATASETS

Supporting datasets for extended validation (not the main focus):

| Folder | Contents |
|--------|----------|
| `ADDITIONAL_samples/` | 4 sample human EEG files |
| `ADDITIONAL_openneuro/` | 5 OpenNeuro datasets |

---

## Download Instructions

### PRIMARY_hbn_human/

```bash
# Download from OpenNeuro ds005508
pip install openneuro-py
openneuro-py download ds005508 --target data/PRIMARY_hbn_human/
```

### PRIMARY_synthetic/

Already included in the repository.
