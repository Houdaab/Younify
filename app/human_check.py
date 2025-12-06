#!/usr/bin/env python3
"""
Human EEG Verification Tool

Determines whether an EEG signal is from a genuine human brain or synthetic.

This tool computes the Human Legitimacy Score (HLS) and classifies signals
as HUMAN (score >= 50) or NOT HUMAN (score < 50).

The classification is purely algorithmic - it analyzes the brainwave signal
characteristics (1/f spectral slope, entropy, channel uniqueness, etc.)
and outputs HUMAN or NOT HUMAN based on the computed score.

Usage:
    python -m app.human_check data/sample.csv
    python -m app.human_check --data-dir data/
    python -m app.human_check file1.csv file2.csv --threshold 75

Author: EEG Legitimacy Team
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loader import load_eeg_csv
from src.preprocess import normalize_channels
from src.hls_score import compute_hls

# Default threshold for human classification (matches hls_score.py)
HUMAN_THRESHOLD = 50

# TODO: in the dataset, we have different fs's for recording patient's signal
def check_human(filepath: Path, fs: float = 256.0) -> dict:
    """
    Check if an EEG file is from a human brain.
    
    Returns dict with:
    - is_human: bool
    - score: float (0-100)
    - verdict: str
    """
    try:
        time, data, channels = load_eeg_csv(filepath)
        data_norm = normalize_channels(data, method="zscore")
        scores = compute_hls(data_norm, fs=fs)
        
        hls = scores["hls"]
        is_human = hls >= HUMAN_THRESHOLD
        
        if hls >= 70:
            verdict = "✅ HUMAN - High confidence"
        elif hls >= 50:
            verdict = "✅ HUMAN - Moderate confidence"
        elif hls >= 35:
            verdict = "⚠️ UNCERTAIN - Borderline, possible artifacts"
        elif hls >= 20:
            verdict = "❌ NOT HUMAN - Likely synthetic/artificial"
        else:
            verdict = "❌ NOT HUMAN - Definitely artificial"
        
        return {
            "filename": filepath.name,
            "is_human": is_human,
            "score": hls,
            "verdict": verdict,
            "components": {
                "PBD": scores["pbd"],
                "NCM": scores["ncm"],
                "MVI": scores["mvi"],
                "TAM": scores["tam"],
                "NSC": scores["nsc"],
            }
        }
    except Exception as e:
        return {
            "filename": filepath.name,
            "error": str(e)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Human EEG Verification")
    parser.add_argument("files", nargs="*", help="CSV files to check")
    parser.add_argument("--data-dir", type=str, help="Directory of CSV files")
    parser.add_argument("--fs", type=float, default=256.0, help="Sampling frequency")
    parser.add_argument("--threshold", type=float, default=50, help="Human threshold (default: 50)")
    args = parser.parse_args()
    
    global HUMAN_THRESHOLD
    HUMAN_THRESHOLD = args.threshold
    
    # Collect files
    files = []
    if args.files:
        files = [Path(f) for f in args.files]
    elif args.data_dir:
        files = sorted(Path(args.data_dir).glob("*.csv"))
    else:
        print("Usage: python -m app.human_check <file.csv> or --data-dir <dir>")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("🧠 HUMAN EEG VERIFICATION")
    print("=" * 60)
    print(f"Threshold: {HUMAN_THRESHOLD}/100")
    print(f"Files: {len(files)}")
    print("=" * 60)
    
    results = []
    humans = 0
    not_humans = 0
    
    print()
    print(f"{'FILE':<35} {'SCORE':>6}  {'RESULT'}")
    print("-" * 60)
    
    for filepath in files:
        result = check_human(filepath, args.fs)
        results.append(result)
        
        if "error" in result:
            print(f"{result['filename']:<35} {'ERR':>6}  ⚠️ {result['error'][:20]}")
        else:
            score = result["score"]
            is_human = "HUMAN" if result["is_human"] else "NOT HUMAN"
            icon = "✅" if result["is_human"] else "❌"
            print(f"{result['filename']:<35} {score:>5.1f}  {icon} {is_human}")
            
            if result["is_human"]:
                humans += 1
            else:
                not_humans += 1
    
    print("-" * 60)
    print()
    print("SUMMARY")
    print(f"  ✅ Human:     {humans}")
    print(f"  ❌ Not Human: {not_humans}")
    print()


if __name__ == "__main__":
    main()

