"""
FastAPI server for EEG Legitimacy Analysis

Accepts EEG data and returns the Human Legitimacy Score.

Usage:
    uvicorn app.server:app --reload --port 8000
    
Endpoints:
    POST /analyze       - Analyze EEG data (JSON)
    POST /analyze/csv   - Analyze EEG data (CSV file upload)
    GET  /health        - Health check
"""

import io
import sys
import uuid
from pathlib import Path
from typing import Annotated, List, Optional, Literal

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse

from app.blockchain import BrainStateNode, BrainStateNodeModel
from app.db import update_chain_document, get_chain_by_id, add_node_to_chain, list_chain_summaries, create_new_chain
from app.models.api import AddNodeRequest
from app.models.internal import ExtraUserData

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.preprocess import normalize_channels
from src.features import extract_all_features
from src.hls_score import compute_hls


# =============================================================================
# Pydantic Models
# =============================================================================

class EEGData(BaseModel):
    """Input model for EEG data."""
    time: list[float] = Field(..., description="Time values")
    channels: list[str] = Field(..., description="Channel names")
    data: list[list[float]] = Field(
        ..., 
        description="EEG data as 2D array (samples x channels)"
    )
    sampling_frequency: float = Field(
        default=256.0, 
        description="Sampling frequency in Hz"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "time": [0.0, 0.004, 0.008, 0.012],
                "channels": ["Fp1", "Fp2", "F3", "F4"],
                "data": [
                    [1.2, 0.8, -0.5, 0.3],
                    [1.1, 0.9, -0.4, 0.2],
                    [1.3, 0.7, -0.6, 0.4],
                    [1.0, 1.0, -0.3, 0.1]
                ],
                "sampling_frequency": 256.0
            }
        }


class ComponentScores(BaseModel):
    """Individual HLS component scores."""
    pbd: float = Field(..., description="Physiological Baseline Deviation (0-1)")
    ncm: float = Field(..., description="Neural Complexity Measures (0-1)")
    mvi: float = Field(..., description="Micro-Variability Index (0-1)")
    tam: float = Field(..., description="Temporal Autocorrelation Measures (0-1)")
    nsc: float = Field(..., description="Neural Signal Consistency (0-1)")


class FeatureResults(BaseModel):
    """Extracted feature statistics."""
    variance: dict[str, float]
    spectral_entropy: dict[str, float]
    fractal_dimension: dict[str, float]
    micro_variability: dict[str, float]


class HLSResponse(BaseModel):
    """Response model for HLS analysis."""
    hls: float = Field(..., description="Human Legitimacy Score (0-100)")
    interpretation: str = Field(..., description="Score interpretation")
    components: ComponentScores
    features: FeatureResults
    metadata: dict = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="EEG Legitimacy API",
    description="Analyze EEG signals and compute Human Legitimacy Scores",
    version="0.1.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Helper Functions
# =============================================================================

def interpret_score(hls: float) -> str:
    """Generate human-readable interpretation of HLS."""
    if hls >= 80:
        return "HIGH - Signal appears to be genuine human EEG"
    elif hls >= 60:
        return "MODERATE - Signal shows some human characteristics"
    elif hls >= 40:
        return "LOW - Signal has questionable authenticity"
    else:
        return "VERY LOW - Signal unlikely to be genuine human EEG"


def analyze_eeg(data: np.ndarray, channels: list[str], fs: float) -> HLSResponse:
    """Run the full analysis pipeline."""
    # Preprocess
    data_norm = normalize_channels(data, method="zscore")
    
    # Extract features
    features = extract_all_features(data_norm, fs=fs)
    
    # Compute HLS
    scores = compute_hls(data_norm, fs=fs)
    
    # Build response
    return HLSResponse(
        hls=round(scores["hls"], 2),
        interpretation=interpret_score(scores["hls"]),
        components=ComponentScores(
            pbd=round(scores["pbd"], 4),
            ncm=round(scores["ncm"], 4),
            mvi=round(scores["mvi"], 4),
            tam=round(scores["tam"], 4),
            nsc=round(scores["nsc"], 4),
        ),
        features=FeatureResults(
            variance={"mean": float(np.mean(features["variance"])), 
                      "std": float(np.std(features["variance"]))},
            spectral_entropy={"mean": float(np.mean(features["spectral_entropy"])), 
                              "std": float(np.std(features["spectral_entropy"]))},
            fractal_dimension={"mean": float(np.mean(features["fractal_dimension"])), 
                               "std": float(np.std(features["fractal_dimension"]))},
            micro_variability={"mean": float(np.mean(features["micro_variability"])), 
                               "std": float(np.std(features["micro_variability"]))},
        ),
        metadata={
            "n_samples": data.shape[0],
            "n_channels": data.shape[1],
            "channels": channels,
            "sampling_frequency": fs,
        }
    )


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


@app.post("/analyze", response_model=HLSResponse, tags=["Analysis"])
async def analyze_json(eeg_data: EEGData):
    """
    Analyze EEG data provided as JSON.
    
    Accepts EEG time series data and returns the Human Legitimacy Score
    along with component scores and extracted features.
    """
    try:
        data = np.array(eeg_data.data)
        
        if data.ndim != 2:
            raise HTTPException(
                status_code=400, 
                detail="Data must be a 2D array (samples x channels)"
            )
        
        if data.shape[1] != len(eeg_data.channels):
            raise HTTPException(
                status_code=400,
                detail=f"Number of channels ({len(eeg_data.channels)}) "
                       f"doesn't match data dimensions ({data.shape[1]})"
            )
        
        return analyze_eeg(data, eeg_data.channels, eeg_data.sampling_frequency)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze/csv", response_model=HLSResponse, tags=["Analysis"])
async def analyze_csv(
    file: Annotated[UploadFile, File(description="CSV file with Time column and EEG channels")],
    sampling_frequency: Annotated[float, Query(description="Sampling frequency in Hz")] = 256.0,
):
    """
    Analyze EEG data from a CSV file upload.
    
    The CSV should have a 'Time' column and one or more EEG channel columns.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, 
            detail="File must be a CSV"
        )
    
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        
        # Find time column
        time_col = None
        for col in df.columns:
            if col.lower() == "time":
                time_col = col
                break
        
        if time_col is None:
            raise HTTPException(
                status_code=400, 
                detail="CSV must contain a 'Time' column"
            )
        
        # Extract channels
        channels = [col for col in df.columns if col != time_col]
        
        if not channels:
            raise HTTPException(
                status_code=400, 
                detail="CSV must contain at least one EEG channel column"
            )
        
        data = df[channels].to_numpy()
        
        return analyze_eeg(data, channels, sampling_frequency)
    
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/redoc")


UPLOAD_DIR = Path(__file__).parent.parent / "uploaded_videos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload", tags=["Video Upload"])
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    extract_audio_flag: bool = True,
    run_safety_analysis: bool = False
):
    """
    Upload a video file for processing.

    - Saves video directly to UPLOAD_DIR
    - Optionally extracts audio in background
    - Optionally runs full safety analysis

    Returns a job_id to track processing status.
    """

    # TODO: check whether video was uploaded by human (do the check with human vs some animals analysis in here)

    # Validate file type
    valid_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
    if not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(valid_extensions)}"
        )

    # Generate safe unique filename
    suffix = Path(file.filename).suffix
    job_id = str(uuid.uuid4())
    video_path = UPLOAD_DIR / f"{job_id}{suffix}"

    try:
        # Save directly to UPLOAD_DIR
        with open(video_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                buffer.write(chunk)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return {
        "message": "Video uploaded successfully",
        "job_id": job_id,
        "filename": video_path.name,
        "path": str(video_path)
    }
# =============================================================================
# Main
# =============================================================================

# ------------------------
# Request Models
# ------------------------



# ------------------------
# Endpoints
# ------------------------

@app.post("/chains/new", response_model=dict)
def create_chain(user_data: ExtraUserData):
    """
    Create a new chain document.
    Returns summary (_id, user info, nodes_count=0)
    """
    return create_new_chain(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        gender=user_data.gender
    )

@app.get("/chains", response_model=List[dict])
def list_chains():
    return list_chain_summaries()

@app.get("/chain/{chain_id}", response_model=dict)
def get_chain(chain_id: str):
    chain = get_chain_by_id(chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")
    return chain


@app.post("/chain/{chain_id}/add_node", response_model=dict)
def add_node(chain_id: str, request: AddNodeRequest):
    doc = get_chain_by_id(chain_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Chain not found")

    # Last node hash
    nodes = doc.get("nodes", [])
    previous_hash = nodes[-1]["hash"] if nodes else ""

    # Create new blockchain node
    node = BrainStateNode(request.state_data, previous_hash)
    node_model = BrainStateNodeModel(**node.to_dict())

    # Add node via DB helper
    added_node = add_node_to_chain(
        chain_id, node_model, first_name=doc["first_name"],
        last_name=doc["last_name"], gender=doc["gender"]
    )

    return {"message": "Node added successfully", "hash": added_node.hash}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
