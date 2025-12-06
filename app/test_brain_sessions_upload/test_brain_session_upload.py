import requests

# Path to the EEG CSV file to upload
csv_file_path = "sample_001.csv.csv"

# User ID (path parameter)
user_id = "a532b355-f29e-48e6-9316-eb66bebcbf25"

# URL of your FastAPI endpoint with user_id in path
url = f"http://localhost:8000/supply_data/{user_id}"

# Open the CSV file in binary mode
with open(csv_file_path, "rb") as f:
    files = {"file": (csv_file_path, f, "text/csv")}
    response = requests.post(url, files=files)

# Print response from server
print(response.status_code)
print(response.json())
