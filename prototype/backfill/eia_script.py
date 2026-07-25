"""
Converting EIA API data to a pandas DataFrame and then to parquet format for storage
"""
# Importing necessary libraries
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()

# Getting the API key from environment variables
BASE = "https://api.eia.gov/v2"
KEY = os.environ["EIA_KEY"]

# Defining params for the EIA API request
params = {
    "api_key": KEY,
    "frequency": "daily", # Only updates once a day
    "data[0]": "value", # value is price 
    "facets[series][]": "RNGWHHD", # Series ID for Henry Hub Natural Gas Spot Price
    "sort[0][column]": "period", # Sort by period (date)
    "sort[0][direction]": "asc", # Sort dates in ascending order
    "start": '2024-01-01', # Oldest date to fetch data from
    "end": '2026-07-01', # Latest date to fetch data from
    "length": 5000, # Safety to ensure we get all necessary data
}

# Fetching the necessary data from the EIA API
r = requests.get(f"{BASE}/natural-gas/pri/fut/data/", params=params, timeout=30)
r.raise_for_status()
gas_data = r.json()

# Converting the data to a pandas DataFrame

gas_df = pd.DataFrame(gas_data['response']['data'])

# Saving the DataFrame to a parquet file for storage
gas_df.to_parquet('../../data/eia_gas_data.parquet', engine = 'pyarrow')

# Verification of the number of rows that loaded
gas_length = len(gas_df)

print(f"Loaded {gas_length} rows of EIA data")
print(gas_df.head())