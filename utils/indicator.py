import requests
import os
from time import sleep
import logging
from datetime import datetime, timedelta, timezone
import urllib.parse
import pandas as pd
import json
import pytz
from typing import List, TypedDict
from collections import deque
from enum import IntEnum, Enum
import pandas_ta as ta
from dataclasses import dataclass, field
import paca_bars as bars

class Direction(Enum):
    UP = 1
    DOWN = 2

class IndType(Enum):
    EMA = 1
    REGRESSION = 2

class TrendType(Enum):
    PCT_CHANGE =1

@dataclass
class Trend():
    symbol: str = field(default=None)
    trendtype: TrendType = field(default=None)
    indicator: IndType = field(default=None)
    direction: Direction = field(default=None)
    price: float = field(default=None)
    change: float = field(default=None)

    def __repr__(self):
        return f" ----------- {self.symbol} Trend --------  \n" \
               f"  trend type  = {self.trendtype.name!r}\n" \
               f"  indicator   = {self.indicator.name!r}\n" \
               f"  direction   = {self.direction.name!r}\n" \
               f"  price       = {self.price}\n" \
               f"  change      = {self.change},\n" \
               f"  -----------------------------------------"


class Trend2(TypedDict):
    symbol: str = field(default=None)
    trendtype: TrendType = field(default=None)
    indicator: IndType = field(default=None)
    direction: Direction = field(default=None)
    price: list[float] = field(default=None)
    change: float = field(default=None)

    def __repr__(self):
        return f" ----------- {self.symbol} Trend --------  \n" \
               f"  trend type  = {self.trendtype.name!r}\n" \
               f"  indicator   = {self.indicator.name!r}\n" \
               f"  direction   = {self.direction.name!r}\n" \
               f"  price       = {self.price.name!r}\n" \
               f"  chane       = {self.change.name!r}\n" \
               f"  -------------------------------------"


## to avoid multiple copy of the dataframe 
## use generate multiple indicators using the same dataframe
## so this indicators class will host many indicators
class Indicators:
    def __init__(self, symbol: str):
        self.symbol=symbol
        self.df: pd.DataFrame = self.get_data()

    def get_data(self):
        return pd.DataFrame(bars.get_10bars(self.symbol, feed="iex"))
    

    def test(self):
        print(type(self.df))
        print(self.df)


    def ema(self, period: int) -> Trend:
        self.df['ema5'] = ta.ema(self.df['c'], period=period)
        # Extract the time part
        self.df["t2"] = pd.to_datetime(self.df["t"], errors='coerce',utc=True)
        self.df['t2_est'] = self.df['t2'].dt.tz_convert('US/Eastern')
        self.df['time'] = self.df['t2_est'].dt.time
        # print(df)
        row = self.df.tail(1).to_dict(orient='records')[0]

        # Calculate the percentage change
        pct = (row['ema5'] - row['c']) / row['c'] 
        # print(row)
        # print(pct)
        t = Trend()
        t.symbol =self.symbol
        t.indicator = IndType.EMA
        t.trendtype = TrendType.PCT_CHANGE
        t.price = row['c']
        t.change = pct
        if  pct <= 0:
            t.direction = Direction.DOWN
        else:
            t.direction = Direction.UP
        print(t)

        
        return t