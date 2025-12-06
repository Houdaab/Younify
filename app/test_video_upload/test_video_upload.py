import requests
from pathlib import Path

# CONFIG
API_URL = "http://127.0.0.1:8000/upload"
VIDEO_NAME = "test.mp4"  # <-- Put your video here

# Get video in same folder
video_path = Path(VIDEO_NAME)

# Open and send
with open(video_path, "rb") as f:
    files = {
        "file": (video_path.name, f, "video/mp4"),
    }

    params = {
        "extract_audio_flag": True,
        "run_safety_analysis": False,
    }

    response = requests.post(API_URL, files=files, params=params)

print("\nStatus code:", response.status_code)
print("Response:")
print(response.json())
