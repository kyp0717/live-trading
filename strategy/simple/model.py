import minutebar as mb
import numpy as np
from sklearn.linear_model import LinearRegression
from supabase import create_client, Client
import os
from enum import Enum
from enum import IntEnum
import logging
import sys

from dotenv import load_dotenv

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

class SignalTrade(Enum):
    Buy = 'buy'
    Sell = 'sell'
    Hold = 'hold'

def fit(symbol: str, feature: str) -> None:
    ## load bar data to postgres
    logging.info(f"Fit: fetching bar data and load to supabase ...")
    mb.paca_get_bar(feed="iex",symbol=symbol)
    mb.paca_get_bar(feed="iex",symbol="SPY")

    supabase_key = os.getenv("SUPABASE_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase: Client = create_client(supabase_url, supabase_key)

    bars = supabase.table("bar_realtime") \
                    .select("*") \
                    .filter('symbol','eq',symbol) \
                    .order('timestamp', desc=True) \
                    .limit(6) \
                   .execute()

    if len(bars.data) < 7:
        logging.info(f"Model: not enough {symbol} bar for fitting ...")
        return None
    
    logging.info(f"Fit: calc slope of price and volume for {symbol}")
    feat = np.array([bar[feature] for bar in bars.data])
    pos = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)

    model = LinearRegression().fit(pos, feat)
    slope = float(model.coef_[0])
    intercept = float(model.intercept_)

    model_data = {
        'symbol': symbol,
        'feature': feature,
        'slope': slope,
        'intercept': intercept
    }
    logging.info(f"Fit: load slope of price and volume for {symbol} to db")
    supabase.table("simple_model").insert(model_data).execute()

def predict(symbol: str) -> SignalTrade:
    # signal = SignalTrade.Hold
    # measure rolling slope

    logging.info(f"Model: fitting ...")
    fit(symbol, "current")
    fit(symbol, "volume")
    fit("SPY", "current")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)


    logging.info(f"Supabase: get indicators ...")
    slope_price = supabase.table("simple_model") \
                    .select("slope") \
                    .filter('symbol','eq',symbol) \
                    .filter('feature','eq','current') \
                    .order('timestamp', desc=True) \
                    .limit(1) \
                   .execute()
    print(slope_price)
    price_indicator = slope_price.data[0]['slope']
    slope_volume = supabase.table("simple_model") \
                    .select("slope") \
                    .filter('symbol','eq',symbol) \
                    .filter('feature','eq','volume') \
                    .order('timestamp', desc=True) \
                    .limit(1) \
                   .execute()
    print(slope_volume)
    volume_indicator = slope_volume.data[0]['slope']
    slope_spy = supabase.table("simple_model") \
                    .select("slope") \
                    .filter('symbol','eq',"SPY") \
                    .filter('feature','eq','current') \
                    .order('timestamp', desc=True) \
                    .limit(1) \
                   .execute()
    spy_price_indicator = slope_spy.data[0]['slope']
    
    logging.info(f"Model: generate trade signal ...")
    if price_indicator > 0 and \
       volume_indicator > 0 and \
       spy_price_indicator > 0:
      return  SignalTrade.Buy
    else:
      return SignalTrade.Sell

      