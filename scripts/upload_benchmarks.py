from pathlib import Path
import requests


API_URL = "http://127.0.0.1:8000"

folder = Path("data/sample_documents")

files = [
    "travel_policy.txt",
    "expense_policy.txt",
    "onboarding_policy.txt",
    "access_policy.txt",
    "incident_response.txt",
    "procurement_policy.txt"
]


for filename in files:

    file_path = folder / filename

    print("\nUploading:", filename)

    with open(file_path, "rb") as file:

        response = requests.post(
            API_URL + "/documents/upload",
            files={"file": (filename, file, "text/plain")},
            timeout=120
        )

    if response.status_code == 200:

        print("Uploaded Successfully")

    elif response.status_code == 409:

        print("Document Already Exists")

    else:

        print("Upload Failed:", response.text)


print("\nDocument Upload Process Completed")