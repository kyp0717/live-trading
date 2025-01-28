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
def paca_get_bars(feed: str, symbol: str) -> List:
    est = pytz.timezone('US/Eastern')
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'

    # Get current time in UTC
    now_utc = datetime.now(timezone.utc)
    # print(f'current time - {now_utc.astimezone(est).strftime(fmt)}')
    # Calculate time 15 minutes ago
    ten_minutes_ago = now_utc - timedelta(minutes=10)
    ten_minutes_ago_iso = ten_minutes_ago.isoformat()  # Generates an ISO 8601/RFC 3339 compatible string

    url_encoded_timestamp = urllib.parse.quote(ten_minutes_ago_iso)
    url_encoded_now = urllib.parse.quote(now_utc.isoformat())
    # print(url_encoded_timestamp)
    # print(f'10 minutes ago - {ten_minutes_ago.astimezone(est).strftime(fmt)}')

    urlsymbol = f"?symbols={symbol}"
    timeframe = "&timeframe=1Min"
    # start="&start=2024-01-03T00%3A00%3A00Z"
    start = f"&start={url_encoded_timestamp}"
    # end="&end=2024-01-04T00%3A00%3A00Z"
    end = f"&end={url_encoded_now}"
    limit="&limit=10"
    feed="&feed=iex"
    adjust="&adjustment=raw"
    sort="&sort=asc"
    endpoint = "https://data.alpaca.markets/v2/stocks/bars"
    url = endpoint + urlsymbol + timeframe + start + end + limit + feed + adjust + sort
    

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
        return data['bars'][symbol]


    




 



