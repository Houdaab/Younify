"""
EEG Physiological State Classification Script

Loads all EEG CSV files from data/, extracts features, classifies mental state,
and generates a results report.

Usage:
    python -m app.classify_states
    python -m app.classify_states --data-dir data/ --output report.txt
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loader import load_eeg_csv
from src.preprocess import normalize_channels
from src.state_features import extract_state_features
from src.state_classifier import StateClassifier, ClassificationResult
from src.hls_score import compute_hls


def process_file(filepath: Path, fs: float = 256.0) -> dict | None:
    """
    Process a single EEG file and return classification results.
    """
    try:
        # Load EEG data
        time, data, channels = load_eeg_csv(filepath)
        
        # Normalize for HLS computation
        data_norm = normalize_channels(data, method="zscore")
        
        # Compute HLS scores for quality validation
        hls_scores = compute_hls(data_norm, fs=fs)
        
        # Extract features for state classification
        features = extract_state_features(data, channels)
        
        # Classify state (with HLS quality check)
        classifier = StateClassifier()
        result = classifier.classify(features, hls_scores=hls_scores)
        
        return {
            "filename": filepath.name,
            "filepath": str(filepath),
            "samples": len(time),
            "channels": len(channels),
            "channel_names": channels,
            "state": result.state.value,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "all_scores": result.scores,
            "hls_score": hls_scores["hls"],
            "ncm_score": hls_scores["ncm"],
            "features": {
                k: v for k, v in features.items() 
                if not isinstance(v, dict)  # Exclude nested dicts for summary
            }
        }
    except Exception as e:
        return {
            "filename": filepath.name,
            "error": str(e)
        }


def generate_report(results: list[dict], output_path: Path | None = None) -> str:
    """
    Generate a formatted results report.
    """
    lines = []
    lines.append("=" * 80)
    lines.append("EEG PHYSIOLOGICAL STATE CLASSIFICATION REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Files processed: {len(results)}")
    lines.append("=" * 80)
    
    # Summary table
    lines.append("\n" + "─" * 90)
    lines.append(f"{'FILENAME':<35} {'STATE':<25} {'CONF':>6} {'HLS':>6} {'NCM':>6}")
    lines.append("─" * 90)
    
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    
    for result in successful:
        conf_str = f"{result['confidence']:.0f}%"
        hls_str = f"{result.get('hls_score', 0):.0f}"
        ncm_str = f"{result.get('ncm_score', 0):.2f}"
        lines.append(f"{result['filename']:<35} {result['state']:<25} {conf_str:>6} {hls_str:>6} {ncm_str:>6}")
    
    for result in failed:
        lines.append(f"{result['filename']:<35} {'ERROR':<25} {'---':>6} {'---':>6} {'---':>6}")
    
    lines.append("─" * 90)
    
    # Detailed results
    lines.append("\n" + "=" * 80)
    lines.append("DETAILED RESULTS")
    lines.append("=" * 80)
    
    for result in successful:
        lines.append(f"\n┌─ {result['filename']}")
        lines.append(f"│  Samples: {result['samples']}, Channels: {result['channels']}")
        lines.append(f"│  HLS: {result.get('hls_score', 0):.1f}/100, NCM: {result.get('ncm_score', 0):.3f}")
        lines.append(f"│")
        lines.append(f"│  STATE: {result['state']}")
        lines.append(f"│  CONFIDENCE: {result['confidence']:.1f}%")
        lines.append(f"│  Reasoning: {result['reasoning']}")
        lines.append(f"│")
        lines.append(f"│  Key Features:")
        lines.append(f"│    • Stability: {result['features']['stability']:.3f}")
        lines.append(f"│    • Coherence: {result['features']['coherence']:.3f}")
        lines.append(f"│    • Global Variability: {result['features']['global_variability']:.3f}")
        lines.append(f"│    • Mean Entropy: {result['features']['mean_entropy']:.3f}")
        lines.append(f"│    • Occipital Ratio: {result['features']['occipital_ratio']:.3f}")
        lines.append(f"│    • Asymmetry: {result['features']['asymmetry']:.3f} ({result['features']['asymmetry_direction']})")
        lines.append(f"│")
        lines.append(f"│  All State Scores:")
        for state, score in sorted(result['all_scores'].items(), key=lambda x: -x[1]):
            bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
            lines.append(f"│    {state:<18} [{bar}] {score:.0f}")
        lines.append(f"└{'─' * 78}")
    
    # Error summary
    if failed:
        lines.append("\n" + "=" * 80)
        lines.append("ERRORS")
        lines.append("=" * 80)
        for result in failed:
            lines.append(f"  • {result['filename']}: {result['error']}")
    
    # State distribution summary
    if successful:
        lines.append("\n" + "=" * 80)
        lines.append("STATE DISTRIBUTION SUMMARY")
        lines.append("=" * 80)
        state_counts = {}
        for r in successful:
            state_counts[r['state']] = state_counts.get(r['state'], 0) + 1
        
        for state, count in sorted(state_counts.items(), key=lambda x: -x[1]):
            pct = count / len(successful) * 100
            bar = "█" * int(pct / 5)
            lines.append(f"  {state:<20} {count:>3} files ({pct:>5.1f}%) {bar}")
    
    lines.append("\n" + "=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    report = "\n".join(lines)
    
    # Save to file if path provided
    if output_path:
        output_path.write_text(report)
    
    return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="EEG Physiological State Classification")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory containing CSV files (default: data/)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for report (optional)"
    )
    parser.add_argument(
        "--json",
        type=str,
        default=None,
        help="Output JSON file for results (optional)"
    )
    parser.add_argument(
        "--exclude",
        type=str,
        nargs="*",
        default=[],
        help="Files to exclude (e.g., --exclude ALAS_Recording01)"
    )
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    
    if not data_dir.exists():
        print(f"Error: Directory not found: {data_dir}")
        sys.exit(1)
    
    # Find CSV files
    csv_files = sorted(data_dir.glob("*.csv"))
    
    # Apply exclusions
    if args.exclude:
        csv_files = [
            f for f in csv_files 
            if not any(exc in f.name for exc in args.exclude)
        ]
    
    if not csv_files:
        print("No CSV files to process.")
        sys.exit(1)
    
    print(f"Processing {len(csv_files)} files...")
    
    # Process all files
    results = []
    for filepath in csv_files:
        print(f"  • {filepath.name}...", end=" ", flush=True)
        result = process_file(filepath)
        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"{result['state']} ({result['confidence']:.0f}%)")
        results.append(result)
    
    # Generate report
    output_path = Path(args.output) if args.output else None
    report = generate_report(results, output_path)
    
    print("\n" + report)
    
    if output_path:
        print(f"\nReport saved to: {output_path}")
    
    # Save JSON if requested
    if args.json:
        json_path = Path(args.json)
        with open(json_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"JSON results saved to: {json_path}")


if __name__ == "__main__":
    main()

