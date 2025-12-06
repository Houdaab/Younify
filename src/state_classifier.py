"""
EEG Physiological State Classifier

Classifies EEG signals into mental states:
- Relaxed
- Focused
- Internal Thought
- Drowsy
- Meditative
- Overstimulated
- Visually Engaged

Uses a rule-based approach with heuristic confidence scoring.
Incorporates signal quality checks to avoid misclassification of noisy data.
"""

from dataclasses import dataclass
from enum import Enum


class MentalState(Enum):
    """Possible physiological mental states."""
    RELAXED = "Relaxed"
    FOCUSED = "Focused"
    INTERNAL_THOUGHT = "Internal Thought"
    DROWSY = "Drowsy"
    MEDITATIVE = "Meditative"
    OVERSTIMULATED = "Overstimulated"
    VISUALLY_ENGAGED = "Visually Engaged"
    UNCERTAIN = "Uncertain (Low Signal Quality)"


@dataclass
class ClassificationResult:
    """Result of state classification."""
    state: MentalState
    confidence: float  # 0-100
    reasoning: str
    scores: dict[str, float]  # Score for each state


class StateClassifier:
    """
    Rule-based EEG physiological state classifier.
    
    Classification is based on feature patterns associated with each state:
    
    - Relaxed: High stability, low variability, balanced coherence
    - Focused: High parietal activation, moderate coherence, low entropy
    - Internal Thought: High entropy, low occipital, asymmetry
    - Drowsy: Very high stability, low variability, decreasing trends
    - Meditative: Very high coherence, high stability, low entropy
    - Overstimulated: High variability, high entropy, low stability
    - Visually Engaged: High occipital activation, high coherence
    """
    
    def __init__(self):
        # Thresholds calibrated for typical EEG patterns
        self.thresholds = {
            "high_stability": 0.7,
            "low_stability": 0.4,
            "high_coherence": 0.6,
            "low_coherence": 0.3,
            "high_variability": 0.8,
            "low_variability": 0.3,
            "high_entropy": 2.5,
            "low_entropy": 1.5,
            "high_occipital_ratio": 1.2,
            "low_occipital_ratio": 0.8,
        }
    
    def _score_relaxed(self, features: dict) -> tuple[float, str]:
        """Score likelihood of Relaxed state."""
        score = 0.0
        reasons = []
        
        # High stability
        if features["stability"] > self.thresholds["high_stability"]:
            score += 30
            reasons.append("high signal stability")
        elif features["stability"] > 0.5:
            score += 15
        
        # Low-moderate variability
        if features["global_variability"] < self.thresholds["low_variability"]:
            score += 25
            reasons.append("low variability")
        elif features["global_variability"] < 0.5:
            score += 15
        
        # Balanced coherence (not too high, not too low)
        if 0.3 < features["coherence"] < 0.6:
            score += 25
            reasons.append("balanced coherence")
        
        # Balanced asymmetry
        if abs(features["asymmetry"]) < 0.1:
            score += 20
            reasons.append("balanced hemispheres")
        
        reasoning = "Relaxed: " + ", ".join(reasons) if reasons else "Relaxed: weak indicators"
        return score, reasoning
    
    def _score_focused(self, features: dict) -> tuple[float, str]:
        """Score likelihood of Focused state."""
        score = 0.0
        reasons = []
        
        # High parietal activation (attention)
        if features["parietal_activation"] > features["global_variability"]:
            score += 30
            reasons.append("elevated parietal activity")
        
        # Moderate-high coherence
        if features["coherence"] > 0.5:
            score += 25
            reasons.append("high coherence")
        
        # Low entropy (ordered processing)
        if features["mean_entropy"] < self.thresholds["low_entropy"]:
            score += 25
            reasons.append("low entropy")
        elif features["mean_entropy"] < 2.0:
            score += 15
        
        # Moderate stability
        if 0.4 < features["stability"] < 0.8:
            score += 20
            reasons.append("moderate stability")
        
        reasoning = "Focused: " + ", ".join(reasons) if reasons else "Focused: weak indicators"
        return score, reasoning
    
    def _score_internal_thought(self, features: dict) -> tuple[float, str]:
        """Score likelihood of Internal Thought state."""
        score = 0.0
        reasons = []
        
        # Higher entropy (complex processing)
        if features["mean_entropy"] > 2.0:
            score += 25
            reasons.append("elevated entropy")
        
        # Lower occipital activation (eyes closed / not visual)
        if features["occipital_ratio"] < self.thresholds["low_occipital_ratio"]:
            score += 30
            reasons.append("reduced occipital activity")
        
        # Some asymmetry (lateralized processing)
        if abs(features["asymmetry"]) > 0.1:
            score += 20
            reasons.append("hemispheric asymmetry")
        
        # Moderate coherence
        if 0.3 < features["coherence"] < 0.6:
            score += 15
        
        # Central activation (internal processing)
        if features["central_activation"] > features["occipital_power"]:
            score += 10
            reasons.append("central > occipital")
        
        reasoning = "Internal Thought: " + ", ".join(reasons) if reasons else "Internal Thought: weak indicators"
        return score, reasoning
    
    def _score_drowsy(self, features: dict) -> tuple[float, str]:
        """Score likelihood of Drowsy state."""
        score = 0.0
        reasons = []
        
        # Very high stability (slow changes)
        if features["stability"] > 0.8:
            score += 35
            reasons.append("very high stability")
        elif features["stability"] > 0.7:
            score += 20
        
        # Very low variability
        if features["global_variability"] < 0.2:
            score += 30
            reasons.append("very low variability")
        elif features["global_variability"] < 0.3:
            score += 15
        
        # Decreasing trend (negative slope)
        if features["mean_slope"] < -0.01:
            score += 20
            reasons.append("decreasing trend")
        
        # Low entropy
        if features["mean_entropy"] < self.thresholds["low_entropy"]:
            score += 15
            reasons.append("low entropy")
        
        reasoning = "Drowsy: " + ", ".join(reasons) if reasons else "Drowsy: weak indicators"
        return score, reasoning
    
    def _score_meditative(self, features: dict) -> tuple[float, str]:
        """Score likelihood of Meditative state."""
        score = 0.0
        reasons = []
        
        # Very high coherence (synchronized)
        if features["coherence"] > self.thresholds["high_coherence"]:
            score += 35
            reasons.append("high coherence")
        elif features["coherence"] > 0.5:
            score += 20
        
        # High stability
        if features["stability"] > self.thresholds["high_stability"]:
            score += 25
            reasons.append("high stability")
        
        # Low entropy (ordered state)
        if features["mean_entropy"] < self.thresholds["low_entropy"]:
            score += 20
            reasons.append("low entropy")
        
        # Balanced asymmetry
        if abs(features["asymmetry"]) < 0.05:
            score += 20
            reasons.append("balanced hemispheres")
        
        reasoning = "Meditative: " + ", ".join(reasons) if reasons else "Meditative: weak indicators"
        return score, reasoning
    
    def _score_overstimulated(self, features: dict) -> tuple[float, str]:
        """Score likelihood of Overstimulated state."""
        score = 0.0
        reasons = []
        
        # High variability
        if features["global_variability"] > self.thresholds["high_variability"]:
            score += 30
            reasons.append("high variability")
        elif features["global_variability"] > 0.5:
            score += 15
        
        # High entropy (chaotic)
        if features["mean_entropy"] > self.thresholds["high_entropy"]:
            score += 30
            reasons.append("high entropy")
        elif features["mean_entropy"] > 2.0:
            score += 15
        
        # Low stability
        if features["stability"] < self.thresholds["low_stability"]:
            score += 25
            reasons.append("low stability")
        
        # High range (large fluctuations)
        if features["mean_range"] > 1.0:
            score += 15
            reasons.append("large amplitude range")
        
        reasoning = "Overstimulated: " + ", ".join(reasons) if reasons else "Overstimulated: weak indicators"
        return score, reasoning
    
    def _score_visually_engaged(self, features: dict) -> tuple[float, str]:
        """Score likelihood of Visually Engaged state."""
        score = 0.0
        reasons = []
        
        # High occipital activation
        if features["occipital_ratio"] > self.thresholds["high_occipital_ratio"]:
            score += 40
            reasons.append("high occipital activation")
        elif features["occipital_ratio"] > 1.0:
            score += 25
        
        # High occipital power
        if features["occipital_power"] > features["central_activation"]:
            score += 20
            reasons.append("occipital > central")
        
        # Moderate-high coherence (visual processing)
        if features["coherence"] > 0.5:
            score += 20
            reasons.append("high coherence")
        
        # Moderate variability
        if 0.3 < features["global_variability"] < 0.7:
            score += 20
            reasons.append("moderate variability")
        
        reasoning = "Visually Engaged: " + ", ".join(reasons) if reasons else "Visually Engaged: weak indicators"
        return score, reasoning
    
    def _check_signal_quality(self, features: dict) -> tuple[bool, str]:
        """
        Check if the signal has characteristics of genuine EEG.
        
        Returns (is_valid, reason) tuple.
        """
        issues = []
        
        # Check for unrealistic variability (too high suggests noise/artifacts)
        if features["global_variability"] > 10:
            issues.append(f"extreme variability ({features['global_variability']:.1f})")
        
        # Check entropy consistency
        # High histogram entropy + low spectral complexity = suspicious
        if features.get("mean_entropy", 0) > 2.5 and features.get("entropy_variance", 0) < 0.01:
            issues.append("inconsistent entropy pattern")
        
        # Check for unrealistic stability-variability combination
        if features["stability"] < 0.3 and features["global_variability"] > 5:
            issues.append("unstable with high variability")
        
        if issues:
            return False, "Signal quality issues: " + ", ".join(issues)
        return True, "Signal quality OK"
    
    def classify(self, features: dict, hls_scores: dict | None = None) -> ClassificationResult:
        """
        Classify the physiological state based on extracted features.
        
        Parameters
        ----------
        features : dict
            Features extracted by extract_state_features().
        hls_scores : dict, optional
            HLS scores from compute_hls() for quality validation.
        
        Returns
        -------
        ClassificationResult
            Classification result with state, confidence, and reasoning.
        """
        # Check signal quality first
        is_valid, quality_reason = self._check_signal_quality(features)
        
        # Also check HLS if provided
        if hls_scores and hls_scores.get("ncm", 1.0) < 0.4:
            is_valid = False
            quality_reason = f"Low neural complexity (NCM={hls_scores['ncm']:.2f}) - signal may not be typical EEG"
        
        # Score each state
        scores = {}
        reasonings = {}
        
        scores[MentalState.RELAXED], reasonings[MentalState.RELAXED] = self._score_relaxed(features)
        scores[MentalState.FOCUSED], reasonings[MentalState.FOCUSED] = self._score_focused(features)
        scores[MentalState.INTERNAL_THOUGHT], reasonings[MentalState.INTERNAL_THOUGHT] = self._score_internal_thought(features)
        scores[MentalState.DROWSY], reasonings[MentalState.DROWSY] = self._score_drowsy(features)
        scores[MentalState.MEDITATIVE], reasonings[MentalState.MEDITATIVE] = self._score_meditative(features)
        scores[MentalState.OVERSTIMULATED], reasonings[MentalState.OVERSTIMULATED] = self._score_overstimulated(features)
        scores[MentalState.VISUALLY_ENGAGED], reasonings[MentalState.VISUALLY_ENGAGED] = self._score_visually_engaged(features)
        
        # Find best state
        best_state = max(scores, key=scores.get)
        best_score = scores[best_state]
        
        # If signal quality is poor, flag as uncertain
        if not is_valid:
            scores[MentalState.UNCERTAIN] = best_score + 10  # Prioritize uncertainty flag
            reasonings[MentalState.UNCERTAIN] = quality_reason
            best_state = MentalState.UNCERTAIN
            best_score = scores[MentalState.UNCERTAIN]
        
        # Normalize confidence (max possible ~100)
        confidence = min(best_score, 100)
        
        # Reduce confidence if quality issues
        if not is_valid:
            confidence = min(confidence, 50)  # Cap at 50% for uncertain
        
        # Convert scores dict to use string keys
        scores_dict = {state.value: score for state, score in scores.items()}
        
        return ClassificationResult(
            state=best_state,
            confidence=confidence,
            reasoning=reasonings[best_state],
            scores=scores_dict
        )


def classify_eeg_state(features: dict) -> ClassificationResult:
    """
    Convenience function to classify EEG state.
    
    Parameters
    ----------
    features : dict
        Features from extract_state_features().
    
    Returns
    -------
    ClassificationResult
        Classification result.
    """
    classifier = StateClassifier()
    return classifier.classify(features)

