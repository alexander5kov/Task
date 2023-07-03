import argparse
import requests
import csv
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from datetime import datetime, timedelta

# Parse command line arguments
parser = argparse.ArgumentParser(description='Transmit CSV to REST API and generate Excel file')
parser.add_argument('-k', '--keys', nargs='+', help='Additional columns to include')
parser.add_argument('-c', '--colored', action='store_true', help='Enable row coloring')
args = parser.parse_args()

# Read the CSV file
with open('vehicles.csv', 'r') as csv_file:
    csv_data = csv.reader(csv_file)
    headers = next(csv_data)
    vehicles = list(csv_data)