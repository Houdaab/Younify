import requests
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
API_URL = "http://127.0.0.1:8000/upload"
VIDEO_NAME = "test.mp4"           # <-- Your video file
USER_ID = "a532b355-f29e-48e6-9316-eb66bebcbf25"  # <-- The user uploading the video

# -----------------------------
# Prepare file
# -----------------------------
video_path = Path(VIDEO_NAME)

with open(video_path, "rb") as f:
    files = {
        "file": (video_path.name, f, "video/mp4"),
    }

    # Query parameters including user_id
    params = {
        "user_id": USER_ID,
        "extract_audio_flag": True,
        "run_safety_analysis": False,
    }

    response = requests.post(API_URL, files=files, params=params)

# -----------------------------
# Output
# -----------------------------
print("\nStatus code:", response.status_code)
print("Response:")
print(response.json())
