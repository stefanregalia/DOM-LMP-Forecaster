"""
Exploration of current and historical PJM demand/load forecast data for the DOM zone
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
    only 25 rows from the API for exploration unless that value is overriden in the kwargs.
    """
    r = requests.get(
        f"{BASE}/{data}", 
        headers=HEADERS, 
        params={"rowCount": 25, "startRow": 1, **kwargs}, timeout = 30)
    r.raise_for_status()
    return r.json()

# Printing 5 rows of the current load forecast data for the DOM zone
load_result = query_pjm('load_frcstd_7_day', forecast_area='DOMINION', rowCount=5)

for l in load_result["items"]:
    print(l)
    
print("------------------------------------------------------------------------------------------------------")

# Printing 5 rows of the historical load forecast data for the DOM zone
hist_results = query_pjm('load_frcstd_hist', forecast_area='DOM', rowCount=5)

for h in hist_results["items"]:
    print(h)