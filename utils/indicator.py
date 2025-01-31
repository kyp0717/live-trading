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
    DOWN = 2

class TrendType(Enum):
    PCT_CHANGE =1

@dataclass
class Trend():
    symbol: str = field(default=None)
    trendtype: TrendType = field(default=None)
    indicator: IndType = field(default=None)
    direction: Direction = field(default=None)
    prices: list[float] = field(default=None)
    change: float = field(default=None)

    def __repr__(self):
        return f" --- {self.symbol} Trend  ----  \n" \
               f"  trend type={self.trendtype.name!r},\n" \
               f"  indicator={self.indicator.name!r}\n" \
               f"  ---------------------------------"


class Trend2(TypedDict):
    symbol: str = field(default=None)
    trendtype: TrendType = field(default=None)
    indicator: IndType = field(default=None)
    direction: Direction = field(default=None)
    prices: list[float] = field(default=None)
    change: float = field(default=None)

    def __repr__(self):
        return f" --- {self.symbol} Trend  ----  \n" \
               f"  trend type={self.trendtype.name!r},\n" \
               f"  indicator={self.indicator.name!r}\n" \
               f"  ---------------------------------"


@dataclass
class Indicator:
    symbol: str
    data: pd.DataFrame

    def ema(self, period: int) -> Trend:
        d = bars.get_10bars(self.symbol, feed="iex")
        df = pd.DataFrame(d)
        df['ema5'] = ta.ema(df['c'], period=period)
        # Extract the time part
        df["t2"] = pd.to_datetime(df["t"], errors='coerce',utc=True)
        df['t2_est'] = df['t2'].dt.tz_convert('US/Eastern')
        df['time'] = df['t2_est'].dt.time
        # print(df)
        row = df.tail(1).to_dict(orient='records')[0]

        # Calculate the percentage change
        pct = (row['ema5'] - row['c']) / row['c'] 
        # print(row)
        # print(pct)
        t = Trend()
        t.symbol =self.symbol
        t.indicator = IndType.EMA
        t.trendtype = TrendType.PCT_CHANGE
        t.prices = [row['c']]
        t.change = pct
        print(t)
        if  pct <= 0:
            t.direction = Direction.DOWN
        else:
            t.direction = Direction.UP
        
        return t