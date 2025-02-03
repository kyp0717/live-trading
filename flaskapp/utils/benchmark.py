# caution: path[0] is reserved for script path (or '' in REPL)
import sys
sys.path.insert(1, '/home/kepl/work/live-trading/flaskapp/utils')

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
from typing import List, TypedDict
from collections import deque
from bokeh.io import output_notebook
import pandas_ta as ta
from dataclasses import dataclass, field
from enum import IntEnum
# from utils import paca_bars as bars
# import paca_bars as bars
from utils import indicator as ind
# import .indicator as ind

# import chart as ct

# Load environment variables from .env file
load_dotenv()
output_notebook()

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

class Benchmark():
    # defining var in init allow for custom variable in each instance
    # when defining var outside of init, the var will be the same in all instance
    def __init__(self, symbol: str, live: bool):
        self.live=live
        self.symbol=symbol
        self.ready=self.check_time()
        # self.ready=True
        # stock_lst = self.get_stock_list()
        self.ema_trend = None
        self.indicator = ind.Indicators(self.symbol, self.live)
        # self.chart = ct.Chart(self.symbol, self.indicator.df)
        # self.test_date = self.derive_test_date()

    def check_time(self):
        today = datetime.now(pytz.timezone('US/Eastern')).date()
        # Create the datetime object for 9:30 AM EST today
        est_datetime = datetime(today.year, today.month, today.day, 9, 40, tzinfo=pytz.timezone('US/Eastern'))
        # Convert to UTC
        market_open_utc_datetime = est_datetime.astimezone(timezone.utc)
        # Get current time in UTC
        now_utc = datetime.now(timezone.utc)

        if now_utc < market_open_utc_datetime:
            return True
        else: return True

    def run(self):
        if self.live == False:
            return self.indicator.ema(period=5)            
        # if self.ready == True:
        #     self.indicator.ema(period=5)
        #     # self.chart.plot()
        #     # self.indicator.test()
        else:
            print('not 9:40am --- more data is needed')


    def get_stock_list(self):
        pass











        
 











    