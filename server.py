import requests
from fastapi import FastAPI, UploadFile, File
from typing import List
from pydantic import BaseModel

app = FastAPI()

class Vehicle(BaseModel):
    rnr: str
    gruppe: str
    kurzname: str
    info: str
    hu: str
    labelIds: List[str]

@app.post("/process_csv")
def process_csv(csv_file: UploadFile = File(...)):

    auth_url = "https://api.baubuddy.de/index.php/login"
    auth_payload = {
        "username": "365",
        "password": "1"
    }
    auth_headers = {
        "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
        "Content-Type": "application/json"
    }
    auth_response = requests.post(auth_url, json=auth_payload, headers=auth_headers)
    auth_data = auth_response.json()
    access_token = auth_data["oauth"]["access_token"]


    csv_content = csv_file.file.read().decode("utf-8")
    csv_lines = csv_content.split("\n")


    if csv_lines[0].startswith("rnr"):
        csv_lines = csv_lines[1:]


    api_url = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
    api_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    api_response = requests.get(api_url, headers=api_headers)
    api_data = api_response.json()


    merged_data = []
    for line in csv_lines:
        if not line:
            continue
        fields = line.split(";")
        rnr = fields[0]
        hu = fields[1]
        label_ids = fields[2].split(",") if len(fields) > 2 else []
        vehicle_data = next((item for item in api_data if item["rnr"] == rnr), None)
        if vehicle_data and hu:
            vehicle_data["hu"] = hu
            vehicle_data["labelIds"] = label_ids
            merged_data.append(vehicle_data)


    label_url = "https://api.baubuddy.de/dev/index.php/v1/labels/{labelId}"
    for item in merged_data:
        for i, label_id in enumerate(item["labelIds"]):
            label_response = requests.get(label_url.format(labelId=label_id), headers=api_headers)
            label_data = label_response.json()
            color_code = label_data.get("colorCode", "")
            item["labelIds"][i] = color_code

    return merged_data
