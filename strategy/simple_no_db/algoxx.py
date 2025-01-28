import modelxx as mod
import minutebarxx as mb

from enum import Enum
from enum import IntEnum

import os
from dotenv import load_dotenv
import time
from supabase import create_client, Client
import logging

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# import pytz
# from datetime import datetime


# Load environment variables from .env file
load_dotenv()

key= os.getenv("APCA_API_KEY_ID")
secret= os.getenv("APCA_API_SECRET_KEY")

# setup alpaca client
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

def sell(symbol: str) -> None:
    market_order_data = MarketOrderRequest(
                        symbol=symbol,
                        qty=1,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.DAY
                        )
    # Market order
    trade_client.submit_order(order_data=market_order_data)

def buy(symbol: str) -> None:
    market_order_data = MarketOrderRequest(
                        symbol=symbol,
                        qty=1,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.DAY
                        )
    # Market order
    trade_client.submit_order(order_data=market_order_data)

def pnl(position: dict, symbol: str) -> float:
    cost_basis = float(position['cost_basis'])
    current_price = float(position['current_price'])
    percentage_change = ((current_price - cost_basis) / cost_basis) 
    logging.info(f"{symbol} PNL - {cost_basis - current_price}")
    logging.info(f"{symbol} PNL - {percentage_change}")
    return percentage_change

def run(symbol: str) -> None:
    logging.info("Algo begins ...")
    algo_iter = 0
    p = PacaPosition.Nonexist
    while True:
        algo_iter += 1
        logging.info(f"------  Algo iteration - {algo_iter}  --------")
        # wait for 1 minute
        time.sleep(4)
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
            # logging.info(f"Algo: {e}")
        
        logging.info(f"{symbol} Position: {p}")
        logging.info(f"{symbol} Model prediction ...")
        signal = mod.predict(symbol)
        logging.info(f"{symbol} Trade signal {signal}")
        if p==PacaPosition.Nonexist:
            if signal == mod.SignalTrade.Buy:
                logging.info(f"{symbol} enter position")
                # preparing market order
                buy(symbol)
        elif p==PacaPosition.Open:
            pct = pnl(position)
            if pct > 0.03:
                logging.info(f"{symbol} close position - profit target reached")
                sell(symbol)
                break
            elif pct < -0.04:
                logging.info(f"{symbol} close position - stop loss")
                sell(symbol)
                break
            else:
                logging.info(f"{symbol} hold position - continue iteration")
                continue
        elif p==PacaPosition.Close:
            logging.info(f"{symbol} Position has been close - exit loop")
            break
    # Check position one last time
    try:
        position = trade_client.get_open_position(symbol)
        if position is None:
            p = PacaPosition.Nonexist
        elif position['qty'] == 0:
            p = PacaPosition.Close
            print("position is closed")
        else:
            p = PacaPosition.Open
            logging.error("Algo: Position is not closed!!!")
    except Exception as e:
        p = PacaPosition.Nonexist
        logging.info(f"Algo: {e}")

    print("Algo: Done")




