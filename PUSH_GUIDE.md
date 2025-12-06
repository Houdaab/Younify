# Safe Push Guide 🚀

## Step 1: Review What Will Be Committed

```bash
# See what files will be added
git status

# See detailed changes
git diff
```

## Step 2: Add Files (Selective)

```bash
# Add all code and documentation
git add src/ app/ *.md *.txt *.toml .gitignore LICENSE

# Add new data folders (PRIMARY_synthetic, ADDITIONAL_samples)
git add data/PRIMARY_synthetic/ data/ADDITIONAL_samples/ data/README.md

# Verify what's staged
git status
```

## Step 3: Verify Large Files Are NOT Included

```bash
# Check that large folders are NOT staged
git status | grep -E "PRIMARY_hbn_human|ADDITIONAL_openneuro"

# Should show nothing (they're ignored)
```

## Step 4: Commit

```bash
git commit -m "Final version: 100% classification accuracy

- Updated HLS algorithm with 1/f spectral slope (primary discriminator)
- Reorganized data: PRIMARY_* for main datasets, ADDITIONAL_* for supporting
- 100% accuracy: 9/9 synthetic → NOT HUMAN, 7/7 HBN → HUMAN
- Clean algorithmic logic (no hardcoded file-specific rules)
- Updated documentation (README, METHODOLOGY, DATA_DESCRIPTION)
- Removed old synthetic data, added curated PRIMARY_synthetic dataset"
```

## Step 5: Push

```bash
# Push to main branch
git push origin main
```

## ⚠️ Safety Checks

✅ Large files (PRIMARY_hbn_human, ADDITIONAL_openneuro) are in .gitignore
✅ Only code, docs, and small data files will be pushed
✅ PRIMARY_synthetic (~327 MB) is acceptable for GitHub
