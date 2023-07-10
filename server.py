import requests
import csv
from fastapi import FastAPI, UploadFile
from typing import List

app = FastAPI()

@app.post('/api/merge')
async def merge_data(file: UploadFile):
    csv_data = await file.read()
    csv_data = csv_data.decode('utf-8').splitlines()
    csv_reader = csv.reader(csv_data)
    header = next(csv_reader)  # Extract header row

    # Request authorization token
    token = get_auth_token()

    # Download resources from API
    api_url = 'https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active'
    api_response = requests.get(api_url, headers={'Authorization': f'Bearer {token}'}).json()

    # Merge resources with CSV data
    merged_data = merge_csv_and_api_data(csv_reader, api_response)

    # Filter out resources without 'hu' field
    filtered_data = filter_data_by_hu(merged_data)

    # Resolve label color codes
    resolve_label_colors(filtered_data, token)

    # Prepare response with header row and merged data
    merged_data.insert(0, header)
    return merged_data

def get_auth_token():
    url = 'https://api.baubuddy.de/index.php/login'
    payload = {
        'username': '365',
        'password': '1'
    }
    headers = {
        'Authorization': 'Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    access_token = response.json().get('oauth', {}).get('access_token')
    return access_token

def merge_csv_and_api_data(csv_data, api_data):
    # Merge CSV data and API response
    merged_data = {}

    for row in csv_data:
        rnr = row[0]
        merged_row = api_data.get(rnr, {})
        merged_row['rnr'] = rnr
        merged_data[rnr] = merged_row

    return list(merged_data.values())

def filter_data_by_hu(data):
    # Filter out resources without 'hu' field
    return [row for row in data if 'hu' in row]

def resolve_label_colors(data, token):
    # Resolve label color codes
    label_api_url = 'https://api.baubuddy.de/dev/index.php/v1/labels/'
    for row in data:
        label_ids = row.get('labelIds', [])
        for label_id in label_ids:
            label_url = f'{label_api_url}{label_id}'
            label_response = requests.get(label_url, headers={'Authorization': f'Bearer {token}'}).json()
            color_code = label_response.get('colorCode')
            if color_code:
                row['colorCode'] = color_code

    return data



