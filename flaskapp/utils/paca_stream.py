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
from alpaca.data.live import StockDataStream


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


from alpaca_trade_api.common import URL
from alpaca_trade_api.stream import Stream

## define co-routine
async def trade_callback(t):
    print('trade', t)


async def quote_callback(q):
    print(type(q))
    # data = json.loads(q)
    # print(type(data))
    # print('quote', q)


# Initiate Class Instance
stream = Stream(os.getenv("APCA_API_KEY_ID"),
                os.getenv("APCA_API_SECRET_KEY"),
                base_url=URL('https://paper-api.alpaca.markets'),
                data_feed='iex')  # <- replace to 'sip' if you have PRO subscription

# subscribing to event
# stream.subscribe_trades(trade_callback, 'AAPL')
stream.subscribe_quotes(quote_callback, 'IBM')

stream.run()