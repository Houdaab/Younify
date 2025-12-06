"""
Batch EEG Legitimacy Scoring

Process specific CSV files or scan a directory.

Usage:
    # Process specific files
    python -m app.batch_score file1.csv file2.csv file3.csv
    
    # Process all files in a directory
    python -m app.batch_score --data-dir ../
    
    # With custom sampling frequency
    python -m app.batch_score file.csv --fs 512
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loader import load_eeg_csv, load_eeg_with_metadata, extract_subject_id
from src.preprocess import normalize_channels
from src.features import extract_all_features
from src.hls_score import compute_hls


def process_file(filepath: Path, fs: float, dataset_dir: Path | None = None) -> dict | None:
    """
    Process a single EEG file and return results with subject ID tracking.
    
    Parameters
    ----------
    filepath : Path
        Path to EEG file
    fs : float
        Sampling frequency
    dataset_dir : Path, optional
        BIDS dataset root directory (for loading participants.tsv)
    """
    try:
        # Try to load with metadata (for BIDS format)
        subject_id = extract_subject_id(filepath)
        
        if subject_id and dataset_dir:
            # Use metadata loader for BIDS datasets
            time, data, channels, metadata = load_eeg_with_metadata(
                filepath, dataset_dir=dataset_dir
            )
            subject_id = metadata.get("subject_id")
        else:
            # Fall back to regular loader
            time, data, channels = load_eeg_csv(filepath)
            subject_id = extract_subject_id(filepath)  # Try to extract from path
        
        # 2. Normalize signal
        data_norm = normalize_channels(data, method="zscore")
        
        # 3. Extract features
        features = extract_all_features(data_norm, fs=fs)
        
        # 4. Compute Human Legitimacy Score
        scores = compute_hls(data_norm, fs=fs)
        
        return {
            "subject_id": subject_id,  # Unique person identifier
            "filename": filepath.name,
            "filepath": str(filepath),
            "hls": scores["hls"],
            "samples": len(time),
            "channels": len(channels),
        }
    except Exception as e:
        print(f"  [ERROR] {filepath.name}: {e}")
        return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch EEG Legitimacy Scoring")
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific CSV files to process"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Directory to scan for CSV files (only used if no files specified)"
    )
    parser.add_argument(
        "--fs",
        type=float,
        default=256.0,
        help="Sampling frequency in Hz (default: 256)"
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default=None,
        help="BIDS dataset root directory (for subject ID tracking and participants.tsv)"
    )
    args = parser.parse_args()
    
    # Determine which files to process
    if args.files:
        # Process specific files provided as arguments
        csv_files = [Path(f) for f in args.files]
        # Verify files exist
        for f in csv_files:
            if not f.exists():
                print(f"Error: File not found: {f}")
                sys.exit(1)
    elif args.data_dir:
        # Scan directory
        data_dir = Path(args.data_dir)
        if not data_dir.exists():
            print(f"Error: Directory not found: {data_dir}")
            sys.exit(1)
        csv_files = sorted(data_dir.glob("*.csv"))
    else:
        # Default: show usage
        print("Usage:")
        print("  python -m app.batch_score file1.csv file2.csv  # specific files")
        print("  python -m app.batch_score --data-dir ../       # scan directory")
        sys.exit(0)
    
    if not csv_files:
        print("No CSV files to process.")
        sys.exit(1)
    
    print("=" * 70)
    print("EEG LEGITIMACY SCORING")
    print("=" * 70)
    print(f"Sampling frequency: {args.fs} Hz")
    print(f"Files to process: {len(csv_files)}")
    print("=" * 70)
    
    # Determine dataset directory
    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else None
    
    # Table header
    print(f"\n{'Subject ID':<15} {'Filename':<40} {'HLS Score':>12}")
    print("-" * 70)
    
    results = []
    
    for filepath in csv_files:
        result = process_file(filepath, args.fs, dataset_dir=dataset_dir)
        
        if result:
            subject_id = result.get('subject_id', 'N/A')
            print(f"{subject_id:<15} {result['filename']:<40} {result['hls']:>10.1f}/100")
            results.append(result)
        else:
            print(f"{'N/A':<15} {filepath.name:<40} {'ERROR':>12}")
    
    # Summary
    print("-" * 64)
    
    if results:
        hls_scores = [r["hls"] for r in results]
        print(f"\nSummary ({len(results)} files processed):")
        print(f"  Mean HLS:  {sum(hls_scores) / len(hls_scores):>6.1f}/100")
        print(f"  Min HLS:   {min(hls_scores):>6.1f}/100")
        print(f"  Max HLS:   {max(hls_scores):>6.1f}/100")
    
    print()


if __name__ == "__main__":
    main()
