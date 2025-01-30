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
from typing import List, TypeAlias
from collections import deque
from enum import IntEnum, Enum
import pandas_ta as ta
from dataclasses import dataclass, field
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, DatetimeTickFormatter


# Load environment variables from .env file
load_dotenv()
output_notebook()

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
class Market(IntEnum):
    Stable = 1
    Rally = 2
    Selloff = 3
    Volatile = 4
    Unknown = 5

class Indicator(Enum):
    ema5 = 1
    ema10 = 2

class Direction(Enum):
    UP = 1
    DOWN = 2

class TrendType(Enum):
    PCT_DELTA =1

@dataclass
class Trend():
    trendtype: TrendType = field(default=None)
    indicator: Indicator = field(default=None)
    direction: Direction = field(default=None)
    prices: list[float] = field(default=None)
    change: float = field(default=None)

class Benchmark:
    # defining var in init allow for custom variable in each instance
    # when defining var outside of init, the var will be the same in all instance
    def __init__(self, symbol: str):
        self.symbol=symbol
        self.ready=self.check_time()
        # self.ready=True
        stock_lst = self.get_stock_list()


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
        
    def trend(self) -> Trend:
        if self.ready==True:
            d = self.get_10bars(feed="iex")
            df = pd.DataFrame(d)
            df['ema5'] = ta.ema(df['c'], length=5)
            # Extract the time part
            df["t2"] = pd.to_datetime(df["t"], errors='coerce',utc=True)
            df['t2_est'] = df['t2'].dt.tz_convert('US/Eastern')
            df['time'] = df['t2_est'].dt.time
            print(df)
            self.plot(df)
            row = df.tail(1).to_dict(orient='records')[0]
 
            # Calculate the percentage change
            pct = (row['ema5'] - row['c']) / row['c'] 
            print(row)
            print(pct)
            t = Trend()
            t.indicator = Indicator.ema5
            t.trendtype = TrendType.PCT_DELTA
            t.prices = [row['c']]
            t.change = pct
            if  pct <= 0:
                t.direction = Direction.DOWN
            else:
                t.direction = Direction.UP
            return t
        else:
            print("not time yet")

    def plot(self,df: pd.DataFrame):
        # Create a ColumnDataSource from the DataFrame
        source = ColumnDataSource(df)

        # Create a figure
        p = figure(title="Line Chart", x_axis_label="x", y_axis_label="y")

        # Add a line glyph
        p.line(x="time", y="c", source=source)
        # Format x-axis labels for EST
        # p.xaxis.formatter = DatetimeTickFormatter(
        #                                 #   years="%d/%m/%Y %H:%M:%S",
        #                                 #   months="%d/%m/%Y %H:%M:%S",
        #                                 #   days="%d/%m/%Y %H:%M:%S",
        #                                   hours="%d/%m/%Y %H:%M:%S",
        #                                 #   hourmin="%d/%m/%Y %H:%M:%S",
        #                                   minutes="%d/%m/%Y %H:%M:%S",
        #                                 #   minsec="%d/%m/%Y %H:%M:%S",
        #                                 #   seconds="%d/%m/%Y %H:%M:%S",
        #                                 #   milliseconds="%d/%m/%Y %H:%M:%S",
        #                                 #   microseconds="%d/%m/%Y %H:%M:%S"
        #                                   )

        p.xaxis.formatter = DatetimeTickFormatter(
                          hours="%H:%M",
                          minutes="%H:%M"
                          )

        # Show the plot
        show(p)


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
        
 











    