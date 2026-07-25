"""
Loading monthly revised LMP data and converting to parquet format for storage
"""

# Importing necessary libraries
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import time
from pathlib import Path

# Setting the data directory path
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Loading environment variables

load_dotenv()

# Getting the API key from environment variables 
BASE = "https://api.pjm.com/api/v1"
HEADERS = {"Ocp-Apim-Subscription-Key": os.environ["PJM_KEY"]}

# DOM zone pnode_id
DOM_PNODE = 34964545

# Query function to get data from PJM API, added retries now for entire backfill
def query_pjm(data, retries = 3, **kwargs):
    """
    Function to query the PJM API for any data and the parameters listed
    """
    for attempt in range(retries):
        try: 
            r = requests.get(
            f"{BASE}/{data}", 
            headers=HEADERS, 
            params={"rowCount": 25, "startRow": 1, **kwargs}, timeout = 30)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            if attempt < retries - 1:
                print(f"Request failed ({e}), retrying in 30 seconds")
                time.sleep(30)
            else:
                raise

# Months to loop over
months = pd.date_range(start='2024-01-01', end='2026-07-01', freq='MS')

for month in months:
    start = month
    end = pd.offsets.MonthEnd(1) + month # Getting the end of the month for the given month

    date_range = f"{start.strftime('%m-%d-%Y')} 00:00 to {end.strftime('%m-%d-%Y')} 23:59" # PJM format

    # Resume check if it ever stops in the middle of a run
    filepath = DATA_DIR / f"rt_da_{month.strftime('%Y_%m')}.parquet"
    if filepath.exists():
        continue

    # Querying the PJM API for the revised LMP data for the DOM zone for the given month
    result = query_pjm('rt_da_monthly_lmps', pnode_id = DOM_PNODE, datetime_beginning_ept = date_range, rowCount = 1000)
    
    revised_df = pd.DataFrame(result['items'])
    revised_df.to_parquet(filepath, engine = 'pyarrow') # Saving to parquet

    print(f"{month.strftime('%Y-%m')}: saved {len(revised_df)} rows")

    time.sleep(20) # Sleep for 20 seconds to avoid hitting the rate limit
 