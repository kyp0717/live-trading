import requests
import os
from dotenv import load_dotenv
from time import sleep
import logging
from datetime import datetime, timedelta, timezone
import urllib.parse
import pandas as pd
import json
import pytz
from typing import List
from collections import deque

# Load environment variables from .env file
load_dotenv()

# Configure logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("algo.log")
    ]
)

def get_bar(symbol: str):
    url = f'https://data.alpaca.markets/v2/stocks/bars/latest?symbols={symbol}'
    # url =  "https://data.alpaca.markets/v2/stocks/bars/latest?symbols=AAPL"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": os.getenv("APCA_API_KEY_ID"),
        "APCA-API-SECRET-KEY": os.getenv("APCA_API_SECRET_KEY")
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    if not data:
        logging.error(f"PACA: no data returned for {symbol}")
        return None
    else:
        return data    

def get_quote(symbol: str) -> List:

    url = f'https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest'
    
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": os.getenv("APCA_API_KEY_ID"),
        "APCA-API-SECRET-KEY": os.getenv("APCA_API_SECRET_KEY")
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    if not data:
        logging.error(f"PACA: no data returned for {symbol}")
        return None
    else:
        return data

class SP500:
    pass
# def spbenchmark():
#     sp500_queue = deque()
#     q = get_quote(symbol='SPY')
    