"""
Exploration of the day-ahead market forecast of hourly LMP's for the DOM zone, which will be the benchmark for 
comparison with my predictions in this project.
"""

# Importing necessary libraries
import os
import requests
from dotenv import load_dotenv

# Loading environment variables

load_dotenv()

# Getting the API key from environment variables 
BASE = "https://api.pjm.com/api/v1"
HEADERS = {"Ocp-Apim-Subscription-Key": os.environ["PJM_KEY"]}

# DOM zone pnode_id
DOM_PNODE = 34964545

# Query function to get data from PJM API
def query_pjm(data, **kwargs):
    """
    Function to query the PJM API for any data and the parameters listed. Queries
    only 25 rows from the API for exploration unless that value is overridden in the kwargs.
    """
    r = requests.get(
        f"{BASE}/{data}", 
        headers=HEADERS, 
        params={"rowCount": 25, "startRow": 1, **kwargs}, timeout = 30)
    r.raise_for_status()
    return r.json()


# Printing 5 rows of the day-ahead LMP data for the DOM zone
da_result = query_pjm("da_hrl_lmps", pnode_id=DOM_PNODE, datetime_beginning_ept="LastWeek", rowCount = 5)

for row in da_result["items"]:
    print(row)