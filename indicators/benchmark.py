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
from enum import IntEnum
import pandas_ta as ta

# Load environment variables from .env file
load_dotenv()
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": os.getenv("APCA_API_KEY_ID"),
    "APCA-API-SECRET-KEY": os.getenv("APCA_API_SECRET_KEY")
}

# Configure logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("algo.log")
    ]
)

## Signal to determine market conditoin
class MarketSignal(IntEnum):
    Stable = 1
    Rally = 2
    Selloff = 3
    Volatile = 4
    Unknown = 5

class MarketStatus():




class Indicator():
    EMA5_PCT = 0.0
    CLOSE = 0.0



class Benchmark:
    # defining var in init allow for custom variable in each instance
    # when defining var outside of init, the var will be the same in all instance
    def __init__(self, symbol: str):
        self.symbol=symbol
        self.ready=self.check_time()
        self.status = {}
        pct_up=0.0
        pct_down=0.0
        pct_change= {}
        window = deque()
        stock_lst = self.get_stock_list()
        signal = MarketStatus.Unknown

    def check_time(self):
        today = datetime.now(pytz.timezone('US/Eastern')).date()
        # Create the datetime object for 9:30 AM EST today
        est_datetime = datetime(today.year, today.month, today.day, 9, 40, tzinfo=pytz.timezone('US/Eastern'))
        # Convert to UTC
        market_open_utc_datetime = est_datetime.astimezone(timezone.utc)
        # Get current time in UTC
        now_utc = datetime.now(timezone.utc)

        if now_utc < market_open_utc_datetime:
            return False
        else: return True 

    def get_stock_list(self):
        pass

    def get_10bars(self,feed: str) -> List:
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

        urlsymbol = f"?symbols={self.symbol}"
        timeframe = "&timeframe=1Min"
        # start="&start=2024-01-03T00%3A00%3A00Z"
        start = f"&start={url_encoded_timestamp}"
        # end="&end=2024-01-04T00%3A00%3A00Z"
        end = f"&end={url_encoded_now}"
        limit="&limit=10"
        feed=f"&feed={feed}"
        adjust="&adjustment=raw"
        sort="&sort=asc"
        endpoint = "https://data.alpaca.markets/v2/stocks/bars"
        url = endpoint + urlsymbol + timeframe + start + end + limit + feed + adjust + sort

        response = requests.get(url, headers=headers)
        data = response.json()
        if not data:
            logging.error(f"PACA: no data returned for {self.symbol}")
            return None
        else:
            return data['bars'][self.symbol]
            # return data
        
    def status(self) -> MarketStatus:
        if self.ready==True:
            d = self.get_10bars(feed="iex")
            df = pd.DataFrame(d)
            df['ema5'] = ta.ema(df['c'], length=5)
            row = df.tail(1).to_dict(orient='records')[0]
 
            # Calculate the percentage change
            pct = (row['ema5'] - row['c']) / row['c'] 
            print(row)
            print(pct)
           
            if (pct >= -0.05 or pct <= 0.05):
                return MarketStatus.Stable
            elif pct > 0.05:
                return MarketStatus.Rally
            elif pct < -0.05:
                return MarketStatus.Selloff
            else:
                return MarketStatus.Unknown
        else:
            print("not time yet")

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
        
 











    