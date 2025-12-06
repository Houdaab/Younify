#!/usr/bin/env python3
"""
HBN Multi-Task EEG Analysis

Goals:
1. Human Legitimacy / Identity Consistency - verify HLS across tasks for same subject
2. State Transitions - track how brain features change between tasks

Tasks analyzed:
- RestingState (passive, eyes open/closed)
- Movie watching: DespicableMe, DiaryOfAWimpyKid, FunwithFractals, ThePresent
- Cognitive: contrastChangeDetection (active attention task)
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import json
import re

import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loader import load_eeg_auto
from src.preprocess import normalize_channels
from src.features import extract_all_features
from src.hls_score import compute_hls
from src.state_features import extract_state_features
from src.state_classifier import classify_eeg_state as classify_state


def get_task_category(task_name: str) -> str:
    """Categorize task into broader groups."""
    task_lower = task_name.lower()
    if "resting" in task_lower:
        return "Resting"
    elif any(movie in task_lower for movie in ["despicable", "diary", "fractals", "present"]):
        return "Movie"
    elif "contrast" in task_lower or "detection" in task_lower:
        return "Cognitive"
    else:
        return "Other"


def load_hbn_eeg(filepath: Path, duration: float = 60.0) -> tuple:
    """Load HBN EEG file with MNE, return subset of data."""
    try:
        import mne
        mne.set_log_level('ERROR')
        
        # Load .set file
        raw = mne.io.read_raw_eeglab(str(filepath), preload=True, verbose=False)
        
        # Get sampling frequency
        sfreq = raw.info['sfreq']
        
        # Get data (first N seconds to speed up analysis)
        n_samples = int(duration * sfreq)
        data = raw.get_data()[:, :n_samples]
        
        # Get channel names (only EEG channels)
        channels = raw.ch_names
        
        # Create time array
        time = np.arange(data.shape[1]) / sfreq
        
        return time, data, channels, sfreq
        
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None, None, None, None


def analyze_subject(subject_dir: Path, duration: float = 60.0) -> Dict[str, Any]:
    """Analyze all tasks for a single subject."""
    subject_id = subject_dir.name
    eeg_dir = subject_dir / "eeg"
    
    results = {
        "subject_id": subject_id,
        "tasks": {},
        "hls_scores": [],
        "state_classifications": [],
    }
    
    # Find all .set files
    set_files = list(eeg_dir.glob("*_eeg.set"))
    
    for set_file in sorted(set_files):
        # Extract task name from filename
        match = re.search(r'task-([^_]+)', set_file.name)
        if not match:
            continue
        task_name = match.group(1)
        
        # Check for run number
        run_match = re.search(r'run-(\d+)', set_file.name)
        run_num = run_match.group(1) if run_match else None
        task_key = f"{task_name}_run{run_num}" if run_num else task_name
        
        print(f"    Processing {task_key}...")
        
        # Load EEG
        time, data, channels, sfreq = load_hbn_eeg(set_file, duration=duration)
        if data is None:
            continue
        
        # Normalize
        data_norm = normalize_channels(data, method="zscore")
        
        # Compute HLS
        hls_result = compute_hls(data_norm, fs=sfreq)
        
        # Extract state features and classify
        state_features = extract_state_features(data_norm, channels)
        state_result = classify_state(state_features)
        
        # Store results
        task_result = {
            "task_name": task_name,
            "task_category": get_task_category(task_name),
            "run": run_num,
            "duration_analyzed": duration,
            "channels": len(channels),
            "samples": data.shape[1],
            "sfreq": sfreq,
            "hls": hls_result,
            "state": state_result.state.value,  # Get string from enum
            "state_confidence": state_result.confidence,
            "state_reasoning": state_result.reasoning,
            "features": {
                "mean_amplitude": float(np.mean(np.abs(data_norm))),
                "global_variance": float(np.var(data_norm)),
                "channel_correlation": float(np.mean(np.corrcoef(data_norm))),
            }
        }
        
        results["tasks"][task_key] = task_result
        results["hls_scores"].append(hls_result["hls"])
        results["state_classifications"].append(state_result.state.value)
    
    # Compute identity consistency metrics
    if results["hls_scores"]:
        results["identity_metrics"] = {
            "mean_hls": float(np.mean(results["hls_scores"])),
            "std_hls": float(np.std(results["hls_scores"])),
            "min_hls": float(np.min(results["hls_scores"])),
            "max_hls": float(np.max(results["hls_scores"])),
            "hls_range": float(np.max(results["hls_scores"]) - np.min(results["hls_scores"])),
            "all_human": all(s >= 50 for s in results["hls_scores"]),
            "consistency_score": 100 - float(np.std(results["hls_scores"])) * 2,  # Higher = more consistent
        }
    
    return results


def analyze_state_transitions(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze how brain states transition between tasks."""
    transitions = {
        "task_sequence": [],
        "state_sequence": [],
        "hls_sequence": [],
        "category_transitions": {},
    }
    
    # Order tasks by category: Resting -> Movie -> Cognitive
    category_order = {"Resting": 0, "Movie": 1, "Cognitive": 2, "Other": 3}
    
    sorted_tasks = sorted(
        results["tasks"].items(),
        key=lambda x: (category_order.get(x[1]["task_category"], 99), x[0])
    )
    
    prev_category = None
    for task_key, task_data in sorted_tasks:
        category = task_data["task_category"]
        state = task_data["state"]
        hls = task_data["hls"]["hls"]
        
        transitions["task_sequence"].append(task_key)
        transitions["state_sequence"].append(state)
        transitions["hls_sequence"].append(hls)
        
        # Track category transitions
        if prev_category and prev_category != category:
            transition_key = f"{prev_category} → {category}"
            if transition_key not in transitions["category_transitions"]:
                transitions["category_transitions"][transition_key] = []
            transitions["category_transitions"][transition_key].append({
                "hls_change": hls - transitions["hls_sequence"][-2] if len(transitions["hls_sequence"]) > 1 else 0,
                "state_from": transitions["state_sequence"][-2] if len(transitions["state_sequence"]) > 1 else None,
                "state_to": state,
            })
        
        prev_category = category
    
    return transitions


def print_report(all_results: List[Dict[str, Any]]):
    """Print comprehensive analysis report."""
    print("\n" + "="*70)
    print("HBN MULTI-TASK EEG ANALYSIS REPORT")
    print("="*70)
    
    # Goal 1: Human Legitimacy / Identity Consistency
    print("\n" + "-"*70)
    print("GOAL 1: HUMAN LEGITIMACY & IDENTITY CONSISTENCY")
    print("-"*70)
    
    for result in all_results:
        subject_id = result["subject_id"]
        metrics = result.get("identity_metrics", {})
        
        print(f"\n📊 Subject: {subject_id}")
        print(f"   Tasks analyzed: {len(result['tasks'])}")
        
        if metrics:
            print(f"\n   HLS Scores:")
            print(f"      Mean:  {metrics['mean_hls']:.1f}")
            print(f"      Range: {metrics['min_hls']:.1f} - {metrics['max_hls']:.1f}")
            print(f"      Std:   {metrics['std_hls']:.1f}")
            
            # Identity verification
            is_human = "✅ HUMAN" if metrics['all_human'] else "❌ INCONSISTENT"
            consistency = "High" if metrics['std_hls'] < 10 else "Medium" if metrics['std_hls'] < 20 else "Low"
            
            print(f"\n   Identity Verification:")
            print(f"      Classification: {is_human}")
            print(f"      Consistency: {consistency} (score: {metrics['consistency_score']:.1f})")
        
        # Task breakdown
        print(f"\n   Task-by-Task HLS:")
        for task_key, task_data in result["tasks"].items():
            hls = task_data["hls"]["hls"]
            category = task_data["task_category"]
            human = "✓" if hls >= 50 else "✗"
            print(f"      {task_key:35} {hls:5.1f} [{category:10}] {human}")
    
    # Goal 2: State Transitions
    print("\n" + "-"*70)
    print("GOAL 2: STATE TRANSITIONS ACROSS TASKS")
    print("-"*70)
    
    for result in all_results:
        if len(result["tasks"]) < 2:
            continue
            
        subject_id = result["subject_id"]
        transitions = analyze_state_transitions(result)
        
        print(f"\n📈 Subject: {subject_id}")
        print(f"\n   State Sequence:")
        for i, (task, state, hls) in enumerate(zip(
            transitions["task_sequence"],
            transitions["state_sequence"],
            transitions["hls_sequence"]
        )):
            arrow = "  →  " if i > 0 else "     "
            print(f"   {arrow}{task:30} State: {state:20} HLS: {hls:.1f}")
        
        # Category transitions
        if transitions["category_transitions"]:
            print(f"\n   Category Transitions:")
            for trans_key, trans_data in transitions["category_transitions"].items():
                avg_change = np.mean([t["hls_change"] for t in trans_data])
                print(f"      {trans_key}: avg HLS change = {avg_change:+.1f}")
    
    # Summary Statistics
    print("\n" + "-"*70)
    print("SUMMARY")
    print("-"*70)
    
    all_hls = []
    all_states = []
    for result in all_results:
        all_hls.extend(result["hls_scores"])
        all_states.extend(result["state_classifications"])
    
    if all_hls:
        print(f"\n   Total recordings analyzed: {len(all_hls)}")
        print(f"   Overall HLS: {np.mean(all_hls):.1f} ± {np.std(all_hls):.1f}")
        print(f"   Human classification rate: {sum(1 for h in all_hls if h >= 50) / len(all_hls) * 100:.0f}%")
        
        # State distribution
        state_counts = {}
        for s in all_states:
            state_counts[s] = state_counts.get(s, 0) + 1
        
        print(f"\n   State Distribution:")
        for state, count in sorted(state_counts.items(), key=lambda x: -x[1]):
            pct = count / len(all_states) * 100
            print(f"      {state}: {count} ({pct:.0f}%)")
    
    print("\n" + "="*70)


def main():
    """Main analysis function."""
    hbn_dir = Path("data/PRIMARY_hbn_human")
    
    if not hbn_dir.exists():
        print("ERROR: HBN data not found at data/PRIMARY_hbn_human/")
        print("Please run the download script first.")
        sys.exit(1)
    
    # Find all subjects
    subject_dirs = sorted([d for d in hbn_dir.iterdir() if d.is_dir() and d.name.startswith("sub-")])
    
    if not subject_dirs:
        print("ERROR: No subjects found in HBN data directory.")
        sys.exit(1)
    
    print("="*70)
    print("HBN MULTI-TASK EEG ANALYSIS")
    print("="*70)
    print(f"\nFound {len(subject_dirs)} subjects")
    print("Analyzing first 60 seconds of each recording...\n")
    
    all_results = []
    
    for subject_dir in subject_dirs:
        print(f"\n📁 Analyzing {subject_dir.name}...")
        result = analyze_subject(subject_dir, duration=60.0)
        all_results.append(result)
    
    # Print report
    print_report(all_results)
    
    # Save results to JSON
    output_file = Path("data/hbn_analysis_results.json")
    
    # Convert numpy types to Python types for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(v) for v in obj]
        return obj
    
    serializable_results = convert_to_serializable(all_results)
    
    with open(output_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")


if __name__ == "__main__":
    main()

