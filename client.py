import requests
import csv
import pandas as pd
from datetime import datetime
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-k', '--keys', nargs='+', help='Additional columns to include')
parser.add_argument('-c', '--colored', action='store_true', default=True, help='Enable row coloring')
args = parser.parse_args()

# Read the CSV file
csv_file = 'vehicles.csv'

# Prepare payload for POST request
files = {'file': open(csv_file, 'rb')}

# Send POST request to server
url = 'http://api.baubuddy.de/api/merge'
response = requests.post(url, files=files)

# Save the response as merged data
merged_data = response.text.splitlines()
csv_reader = csv.reader(merged_data)
header = next(csv_reader)

# Create a DataFrame from the merged data
df = pd.DataFrame(csv_reader, columns=header)

# Sort the rows by the 'gruppe' field if present
if 'gruppe' in df.columns:
    df = df.sort_values(by='gruppe')

# Check if 'hu' column exists before applying operations
if 'hu' in df.columns:
    # Convert 'hu' column to datetime
    df['hu'] = pd.to_datetime(df['hu'])

    # Apply color to the rows based on 'hu' field and the 'colored' flag
    if args.colored:
        today = datetime.today()
        df['color'] = pd.cut((today - df['hu']).dt.days, bins=[-float('inf'), 90, 365, float('inf')],
                             labels=['#007500', '#FFA500', '#b30000'])
        color_mapping = df['color'].dropna().unique().tolist()
        df['color'] = df['color'].apply(lambda x: x if x in color_mapping else '')

# Select the 'rnr' field as a column if it exists
if 'rnr' in df.columns:
    df = df[['rnr']]

# Add additional columns based on the input arguments
if args.keys:
    for key in args.keys:
        df[key] = df.get(key, '')

# Export the DataFrame to Excel
filename = f'vehicles_{datetime.now().isoformat()[:10]}.xlsx'
df.to_excel(filename, index=False)
print(f'Excel file "{filename}" created successfully.')










