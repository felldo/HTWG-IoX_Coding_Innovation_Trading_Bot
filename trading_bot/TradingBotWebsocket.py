# socket manager using threads
import asyncio

import binance
from binance import ThreadedWebsocketManager, ThreadedDepthCacheManager, Client
import os

from datetime import datetime, timedelta
from dateutil import tz
from pymongo import MongoClient, database
from pymongo.collection import Collection

from trading_bot.strategies.BollingerBand import BollingerBand
from trading_bot.strategies.MACD import MACD
from trading_bot.strategies.StrategyReturnType import StrategyReturnType


def get_amount_of_data_from_interval(interval: str) -> int:
    if interval == "1m":
        return 1
    elif interval == "3m":
        return 3
    elif interval == "5m":
        return 5
    elif interval == "15m":
        return 15
    elif interval == "30m":
        return 30
    elif interval == "1h":
        return 60
    elif interval == "2h":
        return 2 * 60
    elif interval == "4h":
        return 4 * 60
    elif interval == "6h":
        return 6 * 60
    elif interval == "8h":
        return 8 * 60
    elif interval == "12h":
        return 12 * 60
    elif interval == "1d":
        return 24 * 60
    elif interval == "3d":
        return 3 * 24 * 60
    elif interval == "1w":
        return 7 * 24 * 60
    elif interval == "1M":
        return 30 * 24 * 60


def build_thread(symbol: str, stop_event, algorithm: str, client: binance.Client, interval: str, trading_bot_db: database.Database):
    print('Start Thread for: ', symbol)

    twm = ThreadedWebsocketManager(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_SECRET'])

    bb = BollingerBand()
    macd = MACD()
    print("++++++++++++++++++++++++++++++++++++++")
    if algorithm == "BB":
        timestamp_in_millis = int((datetime.now() - timedelta(minutes=get_amount_of_data_from_interval(interval) * 20)).timestamp() * 1000)
        prefetchedData = client.get_historical_klines(symbol, interval, timestamp_in_millis)

        for kline in prefetchedData:
            bb.trade(kline[0], float(kline[1]), float(kline[4]))
            print(len(bb.lastTwenty))
    elif algorithm == "MACD":
        timestamp_in_millis = int((datetime.now() - timedelta(minutes=get_amount_of_data_from_interval(interval))).timestamp() * 1000)
        prefetchedData = client.get_historical_klines(symbol, interval, timestamp_in_millis)
        # TODO:
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        if stop_event.is_set():
            print("TRYING TO STOP")
            twm.stop()
            return
        # print("MESSAGE RECEIVED")
        # event_time = datetime.fromtimestamp(msg["E"] / 1000).astimezone(tz.gettz('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S')
        # print(f"message type: {msg['e']}")
        # print(msg)
        # print(event_time, "\t", msg)
        if algorithm == "BB":
            check_trading_action(bb.trade(msg["k"]["t"], float(msg["k"]["o"]), float(msg["k"]["c"])), symbol, trading_bot_db)
        elif algorithm == "MACD":
            check_trading_action(macd.trade(msg["k"]["E"], float(msg["k"]["c"])), symbol, trading_bot_db)
            # print("Replace with function")

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol, interval=interval)

    print("THREAD JOIN")
    twm.join()


def check_trading_action(trade_action: StrategyReturnType, coin_name: str, trading_bot_db: database.Database):
    if trade_action == StrategyReturnType.SELL:
        sell(coin_name, trading_bot_db)
    elif trade_action == StrategyReturnType.BUY:
        buy(coin_name, trading_bot_db)


def buy(coin_name: str, trading_bot_db: database.Database):
    trades_collection: Collection = trading_bot_db.trades
    """
    trades_collection.insert_one({
        "action":"buy",
        "time":"",
        "price":"",
        "quantity":"",
        "symbol":"",
    })
    """

def sell(coin_name: str, trading_bot_db: database.Database):
    print()
