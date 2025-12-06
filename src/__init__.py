"""
EEG Legitimacy Analysis Package

A comprehensive toolkit for analyzing EEG signals and determining their authenticity.

Modules:
    loader: Load EEG data from various formats (CSV, EDF)
    preprocess: Signal preprocessing and normalization
    features: Basic feature extraction (variance, entropy, etc.)
    hls_score: Human Legitimacy Score computation
    state_features: Features for mental state classification
    state_classifier: Mental state classification
    synthetic_eeg: Synthetic signal generation for testing
    model_zoo: Machine learning model templates
"""

__version__ = "1.0.0"
__author__ = "EEG Legitimacy Team"

from .loader import load_eeg_csv, load_eeg_auto
from .preprocess import normalize_channels
from .hls_score import compute_hls
from .features import extract_all_features
from .state_features import extract_state_features
from .state_classifier import StateClassifier, classify_eeg_state

__all__ = [
    "load_eeg_csv",
    "load_eeg_auto",
    "normalize_channels",
    "compute_hls",
    "extract_all_features",
    "extract_state_features",
    "StateClassifier",
    "classify_eeg_state",
]

