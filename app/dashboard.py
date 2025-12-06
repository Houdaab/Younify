#!/usr/bin/env python3
"""
EEG Analysis Dashboard

Interactive dashboard for comparing Real vs Synthetic EEG signals.
Displays Human Legitimacy Scores and signal visualizations.

Usage:
    streamlit run app/dashboard.py

Author: EEG Legitimacy Team
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.loader import load_eeg_csv
from src.preprocess import normalize_channels
from src.hls_score import compute_hls


# Page config
st.set_page_config(
    page_title="Real vs Fake EEG",
    page_icon="🧠",
    layout="wide"
)

# Threshold (matches hls_score.py)
HUMAN_THRESHOLD = 50

# Sampling rates for different data sources
SAMPLING_RATES = {
    "openneuro_eyes_closed": 500.0,
    "default": 256.0
}


def load_and_score(filepath: Path, fs: float = 256.0) -> dict | None:
    """Load file and compute HLS."""
    try:
        time, data, channels = load_eeg_csv(filepath)
        data_norm = normalize_channels(data, method="zscore")
        scores = compute_hls(data_norm, fs=fs)
        return {
            "time": time,
            "data": data_norm,
            "channels": channels,
            "scores": scores,
            "filename": filepath.name
        }
    except:
        return None


def create_signal_plot(time, data, channels, title, color):
    """Create a multi-channel EEG plot."""
    fig = go.Figure()
    
    n_channels = min(4, len(channels))  # Show first 4 channels
    
    for i in range(n_channels):
        offset = i * 4  # Vertical offset for stacking
        fig.add_trace(go.Scatter(
            x=time[:1000],  # First 1000 samples
            y=data[:1000, i] + offset,
            mode='lines',
            name=channels[i],
            line=dict(color=color, width=1),
            showlegend=True
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#1f1f1f")),
        xaxis_title="Time (s)",
        yaxis_title="Amplitude (normalized)",
        height=350,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#1f1f1f"),
        margin=dict(l=50, r=20, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    fig.update_xaxes(gridcolor="#e0e0e0")
    fig.update_yaxes(gridcolor="#e0e0e0", showticklabels=False)
    
    return fig


def create_score_gauge(score, title, is_human):
    """Create a gauge for the human score."""
    color = "#4CAF50" if is_human else "#F44336"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': '/100', 'font': {'size': 40, 'color': color}},
        title={'text': title, 'font': {'size': 16, 'color': '#1f1f1f'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#1f1f1f'},
            'bar': {'color': color},
            'bgcolor': "white",
            'steps': [
                {'range': [0, 70], 'color': '#ffcdd2'},
                {'range': [70, 100], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "#333", 'width': 3},
                'thickness': 0.8,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        paper_bgcolor="white",
        font=dict(color="#1f1f1f"),
        margin=dict(l=30, r=30, t=50, b=20)
    )
    
    return fig


def create_component_bars(scores, color):
    """Create horizontal bar chart for HLS components."""
    components = ['PBD', 'NCM', 'MVI', 'TAM', 'NSC']
    values = [scores['pbd'], scores['ncm'], scores['mvi'], scores['tam'], scores['nsc']]
    
    fig = go.Figure(go.Bar(
        y=components,
        x=values,
        orientation='h',
        marker_color=color,
        text=[f"{v:.2f}" for v in values],
        textposition='outside',
        textfont=dict(color="#1f1f1f", size=12)
    ))
    
    fig.update_layout(
        height=200,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#1f1f1f"),
        xaxis=dict(range=[0, 1.1], gridcolor="#e0e0e0", title="Score"),
        yaxis=dict(gridcolor="#e0e0e0"),
        margin=dict(l=50, r=50, t=20, b=30)
    )
    
    return fig


def main():
    # Header
    st.markdown("""
    <h1 style='text-align: center; color: #1E88E5;'>🧠 Real vs Fake EEG Comparison</h1>
    <p style='text-align: center; color: #666;'>Side-by-side analysis of human vs synthetic brain signals</p>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # File paths (try new names first, fallback to old for compatibility)
    real_dir = Path("data/ADDITIONAL_samples")
    if not real_dir.exists():
        real_dir = Path("data/real")  # Fallback
    
    synthetic_dir = Path("data/PRIMARY_synthetic")
    if not synthetic_dir.exists():
        synthetic_dir = Path("data/synthetic_hbn_format")  # Fallback
        if not synthetic_dir.exists():
            synthetic_dir = Path("data/synthetic")  # Old fallback
    
    # Get file lists
    real_files = sorted(real_dir.glob("*.csv")) if real_dir.exists() else []
    synthetic_files = sorted(synthetic_dir.glob("*.csv")) if synthetic_dir.exists() else []
    
    if not real_files:
        st.warning(f"No real EEG files found in {real_dir}/")
        return
    if not synthetic_files:
        st.warning(f"No synthetic files found in {synthetic_dir}/")
        return
    
    # Selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧠 Real EEG (Human)")
        real_file = st.selectbox("Select real EEG file", real_files, format_func=lambda x: x.name, key="real")
    
    with col2:
        st.markdown("### 🤖 Synthetic (Fake)")
        fake_file = st.selectbox("Select synthetic file", synthetic_files, format_func=lambda x: x.name, key="fake")
    
    st.divider()
    
    # Load data
    real_data = load_and_score(real_file)
    fake_data = load_and_score(fake_file)
    
    if not real_data or not fake_data:
        st.error("Error loading files")
        return
    
    # HUMAN SCORES - Big display
    st.markdown("## 📊 Human Legitimacy Scores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        is_human = real_data["scores"]["hls"] >= HUMAN_THRESHOLD
        verdict = "✅ HUMAN" if is_human else "❌ NOT HUMAN"
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #e8f5e9, #c8e6c9); 
                    padding: 20px; border-radius: 15px; text-align: center;
                    border: 3px solid #4CAF50;'>
            <h2 style='color: #2E7D32; margin: 0;'>{verdict}</h2>
            <h1 style='color: #1B5E20; margin: 10px 0; font-size: 3rem;'>
                {real_data["scores"]["hls"]:.1f}
            </h1>
            <p style='color: #388E3C; margin: 0;'>{real_data["filename"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        is_human = fake_data["scores"]["hls"] >= HUMAN_THRESHOLD
        verdict = "✅ HUMAN" if is_human else "❌ NOT HUMAN"
        bg_color = "#e8f5e9" if is_human else "#ffebee"
        border_color = "#4CAF50" if is_human else "#F44336"
        text_color = "#2E7D32" if is_human else "#C62828"
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ffebee, #ffcdd2); 
                    padding: 20px; border-radius: 15px; text-align: center;
                    border: 3px solid #F44336;'>
            <h2 style='color: #C62828; margin: 0;'>{verdict}</h2>
            <h1 style='color: #B71C1C; margin: 10px 0; font-size: 3rem;'>
                {fake_data["scores"]["hls"]:.1f}
            </h1>
            <p style='color: #D32F2F; margin: 0;'>{fake_data["filename"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <p style='text-align: center; color: #666; margin-top: 10px;'>
        Threshold: <strong>{HUMAN_THRESHOLD}/100</strong> — Above = Human, Below = Not Human
    </p>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # SIGNAL COMPARISON
    st.markdown("## 📈 Signal Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_signal_plot(
            real_data["time"], real_data["data"], real_data["channels"],
            "Real Human EEG", "#4CAF50"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_signal_plot(
            fake_data["time"], fake_data["data"], fake_data["channels"],
            "Synthetic Signal", "#F44336"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # COMPONENT BREAKDOWN
    st.markdown("## 🔬 Score Components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Real EEG Components")
        fig = create_component_bars(real_data["scores"], "#4CAF50")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Synthetic Components")
        fig = create_component_bars(fake_data["scores"], "#F44336")
        st.plotly_chart(fig, use_container_width=True)
    
    # Component explanation
    with st.expander("📖 What do the components mean?"):
        st.markdown("""
        | Component | Full Name | What It Measures |
        |-----------|-----------|------------------|
        | **PBD** | Physiological Baseline Deviation | Variance patterns typical of biological signals |
        | **NCM** | Neural Complexity Measures | Spectral entropy - real EEG has specific frequency patterns |
        | **MVI** | Micro-Variability Index | Sample-to-sample variations in the signal |
        | **TAM** | Temporal Autocorrelation | How the signal correlates with itself over time |
        | **NSC** | Neural Signal Consistency | Cross-channel correlation and frequency bands |
        """)
    
    st.divider()
    
    # ALL FILES SUMMARY
    st.markdown("## 📋 All Files Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Real EEG Files")
        for f in real_files:
            data = load_and_score(f)
            if data:
                score = data["scores"]["hls"]
                icon = "✅" if score >= HUMAN_THRESHOLD else "❌"
                st.markdown(f"{icon} **{f.name}**: {score:.1f}/100")
    
    with col2:
        st.markdown("#### Synthetic Files")
        for f in synthetic_files:
            data = load_and_score(f)
            if data:
                score = data["scores"]["hls"]
                icon = "✅" if score >= HUMAN_THRESHOLD else "❌"
                st.markdown(f"{icon} **{f.name}**: {score:.1f}/100")


if __name__ == "__main__":
    main()

