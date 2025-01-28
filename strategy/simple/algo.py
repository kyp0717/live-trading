import model as mod
from enum import Enum
from enum import IntEnum
from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv
import time
from supabase import create_client, Client
import logging

# Load environment variables from .env file
load_dotenv()

key= os.getenv("APCA_API_KEY_ID")
secret= os.getenv("APCA_API_SECRET_KEY")

# setup clients
trade_client = TradingClient(api_key=key, secret_key=secret, paper=True)

# Configure logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("algo.log")
    ]
)

class PacaPosition(Enum):
    Open = 'open'
    Close = 'close'
    Nonexist = 'nonexist'


def run_simple_model(symbol: str) -> None:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    logging.info("Algo: algo begins ...")

    p = PacaPosition.Nonexist
    while True:
        try:
            position = trade_client.get_open_position(symbol)
            if position is None:
                p = PacaPosition.Nonexist
            elif position['qty'] == 0:
                p = PacaPosition.Close
                print("position is closed")
            else:
                p = PacaPosition.Open
        except Exception as e:
            p = PacaPosition.Nonexist
            bar_count = supabase.table("bar_realtime") \
                            .select("*", count="exact", head=True).execute()
            
            logging.info(f"Algo: {e}")
            logging.info(f"Algo: Waiting for 15 seconds")
            logging.info(f"Algo: number of bars - {bar_count}")
            time.sleep(5)

        logging.info(f"Algo: begin prediction ...")
        signal = mod.predict(symbol)
        if signal == mod.SignalTrade.Buy:
            if p==PacaPosition.Nonexist:
                logging.info("Algo: Open positon on {symbol}-  Submitting order")
                trade_client.submit_order(symbol, 1, 'buy', 'market', 'gtc')
            elif p==PacaPosition.Open:
                continue
        elif signal == mod.SignalTrade.Sell:
             trade_client.submit_order(symbol, 1, 'sell', 'market', 'gtc')
             break
        
    print("Algo: Done")



