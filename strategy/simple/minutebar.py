import requests
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from time import sleep
import logging

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

def paca_get_bar(feed: str, symbol: str) -> None:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    endpoint = "https://data.alpaca.markets/v2/stocks/bars/latest"
    url = f"{endpoint}?symbols={symbol}&feed={feed}"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": os.getenv("APCA_API_KEY_ID"),
        "APCA-API-SECRET-KEY": os.getenv("APCA_API_SECRET_KEY")
    }

    logging.info(f"PACA: fetching bar data for {symbol} ...")
    response = requests.get(url, headers=headers)
    data = response.json()
    bar = data['bars'][symbol]
    bar = {
    'symbol': symbol,
    'current': bar['c'],
    'high': bar['h'],
    'low': bar['l'],
    'volume': bar['v'],
    'vw': bar['vw'],
    'open': bar['o'],
    'n':bar['n'],
    'timestamp': bar['t']
    }

    ## get latest bar from postgres
    logging.info(f"Supabase: load bar for {symbol} ...")
    db_bar = supabase.table("bar_realtime") \
                .select("*") \
                .filter('symbol','eq',symbol) \
                .order('timestamp', desc=True) \
                .limit(1) \
                .execute()
    
    if db_bar.count == None:
        supabase.table("bar_realtime").insert(bar).execute()
        return None
    if db_bar.data[0]['timestamp'] <= bar['timestamp']:
        supabase.table("bar_realtime").insert(bar).execute()
        return None

 
def paca_get_history_bar(feed: str, symbol: str) -> None:
    endpoint = "https://data.alpaca.markets/v2/stocks/bars"
    url =f"{endpoint}?symbols={symbol}&timeframe=1Min&start=2024-01-03T00%3A00%3A00Z&end=2024-01-04T00%3A00%3A00Z&limit=50&adjustment=raw&feed=sip&sort=asc"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": os.getenv("APCA_API_KEY_ID"),
        "APCA-API-SECRET-KEY": os.getenv("APCA_API_SECRET_KEY")
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    bars = data['bars'][symbol]
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)

    for i in bars:
        bar = {
        'symbol': symbol,
        'current': i['c'],
        'high': i['h'],
        'low': i['l'],
        'volume': i['v'],
        'vw': i['vw'],
        'open': i['o'],
        'n':i['n'],
        'timestamp': i['t']
        }

        supabase.table("bar_history").insert(bar).execute()





