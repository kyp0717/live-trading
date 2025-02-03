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
from enum import enum

# Load environment variables from .env file
load_dotenv()

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": os.getenv("APCA_API_KEY_ID"),
    "APCA-API-SECRET-KEY": os.getenv("APCA_API_SECRET_KEY")
}

class Timeframe(enum):
    TODAY = 1
    PAST = 2

def derive_date(dt: Timeframe ):
    est = pytz.timezone('US/Eastern')
    # fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    if dt == Timeframe.Today:
        # Get current time in UTC
        utc_dt = datetime.now(timezone.utc)
    else:
        ## date -- year, month, day, hour, minute, timezone
        est_dt = datetime(2025, 1, 15, 9, 40, est)
        utc_dt = est_dt.astimezone(timezone.utc)

    # print(f'current time - {now_utc.astimezone(est).strftime(fmt)}')
    # Calculate time 15 minutes ago
    ten_minutes_ago = utc_dt - timedelta(minutes=10)
    ten_minutes_ago_iso = ten_minutes_ago.isoformat()  # Generates an ISO 8601/RFC 3339 compatible string

    url_encoded_past = urllib.parse.quote(ten_minutes_ago_iso)
    url_encoded_now = urllib.parse.quote(utc_dt.isoformat())
    return (url_encoded_past, url_encoded_now)

def get_bars_today(symbol: str, feed: str) -> List:
    (start_dt_utc, end_dt_utc) = derive_date(Timeframe.TODAY)
    urlsymbol = f"?symbols={symbol}"
    timeframe = "&timeframe=1Min"
    # start="&start=2024-01-03T00%3A00%3A00Z"
    start = f"&start={start_dt_utc}"
    # end="&end=2024-01-04T00%3A00%3A00Z"
    end = f"&end={end_dt_utc}"
    limit="&limit=10"
    feed=f"&feed={feed}"
    adjust="&adjustment=raw"
    sort="&sort=asc"
    endpoint = "https://data.alpaca.markets/v2/stocks/bars"
    url = endpoint + urlsymbol + timeframe + start + end + limit + feed + adjust + sort

    response = requests.get(url, headers=headers)
    data = response.json()
    if not data:
        logging.error(f"PACA: no data returned for {symbol}")
        return None
    else:
        return data['bars'][symbol]
        # return data


def get_bars_past(feed: str, symbol: str):
    (start_dt_utc, end_dt_utc) = derive_date(Timeframe.PAST)
    urlsymbol = f"?symbols={symbol}"
    timeframe = "&timeframe=1Min"
    # start="&start=2024-01-03T00%3A00%3A00Z"
    start = f"&start={start_dt_utc}"
    # end="&end=2024-01-04T00%3A00%3A00Z"
    end = f"&end={end_dt_utc}"
    limit="&limit=10"
    feed=f"&feed={feed}"
    adjust="&adjustment=raw"
    sort="&sort=asc"
    endpoint = "https://data.alpaca.markets/v2/stocks/bars"
    url = endpoint + urlsymbol + timeframe + start + end + limit + feed + adjust + sort

    response = requests.get(url, headers=headers)
    data = response.json()
    if not data:
        logging.error(f"PACA: no data returned for {symbol}")
        return None
    else:
        return data['bars'][symbol]
        # return data


def get_bar(self):
    url = f'https://data.alpaca.markets/v2/stocks/bars/latest?symbols={self.symbol}'
    response = requests.get(url, headers=headers)

    data = response.json()
    if not data:
        logging.error(f"PACA: unable to get latest bar for {self.symbol}")
        return None
    else:
        return data    
    
def get_quote(self,symbol: str) -> List:
    url = f'https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest'
    
    response = requests.get(url, headers=headers)
    data = response.json()
    if not data:
        logging.error(f"PACA: no data returned for {symbol}")
        return None
    else:
        return data