# socket manager using threads
import asyncio

import binance
#from binance import ThreadedWebsocketManager, ThreadedDepthCacheManager, Client
from python_binance import ThreadedWebsocketManager, ThreadedDepthCacheManager, Client
import os

from datetime import datetime, timedelta
from pymongo import database
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


def build_thread(symbol: str, stop_event, algorithm: str, client: binance.Client, interval: str,
                 trading_bot_db: database.Database):
    print('Start Thread for: ', symbol)

    twm = ThreadedWebsocketManager(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_SECRET'])

    bb = BollingerBand()
    macd = MACD()
    print("++++++++++++++++++++++++++++++++++++++")
    if algorithm == "BB":
        timestamp_in_millis = int(
            (datetime.now() - timedelta(minutes=get_amount_of_data_from_interval(interval) * 20)).timestamp() * 1000)
        prefetched_data = client.get_historical_klines(symbol, interval, timestamp_in_millis)

        for kline in prefetched_data:
            bb.trade(kline[0], float(kline[1]), float(kline[4]))
            print(len(bb.lastTwenty))
    elif algorithm == "MACD":
        timestamp_in_millis = int(
            (datetime.now() - timedelta(minutes=get_amount_of_data_from_interval(interval) * 100)).timestamp() * 1000)
        prefetched_data = client.get_historical_klines(symbol, interval, timestamp_in_millis)

        #print(prefetchedData)
        for kline in prefetched_data:
            macd.trade(kline[0], float(kline[4]))
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
            print(msg)
            check_trading_action(bb.trade(msg["k"]["t"], float(msg["k"]["o"]), float(msg["k"]["c"])), symbol,
                                 trading_bot_db, msg)
        elif algorithm == "MACD":
            check_trading_action(macd.trade(msg["k"]["t"], float(msg["k"]["c"])), symbol, trading_bot_db, msg)

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol, interval=interval)

    print("THREAD JOIN")
    twm.join()


def check_trading_action(trade_action: StrategyReturnType, coin_name: str, trading_bot_db: database.Database, msg):
    if trade_action == StrategyReturnType.SELL:
        sell(coin_name, trading_bot_db, msg)
    elif trade_action == StrategyReturnType.BUY:
        buy(coin_name, trading_bot_db, msg)


lastBuyPrices = {}


def buy(coin_name: str, trading_bot_db: database.Database, msg):
    trades_collection: Collection = trading_bot_db.trades
    wallet_collection: Collection = trading_bot_db.wallet

    coin_wallet = wallet_collection.find_one({"SYMBOL": coin_name})

    money = 0
    quantity = 0
    # if coin is not in our wallet => create coin and give it 100k for trading
    if coin_wallet is None:
        wallet_collection.insert_one({"SYMBOL": coin_name, "QUANTITY": quantity, "MONEY": 100000})
        money = 100000
    else:
        money = coin_wallet.get("MONEY")
        quantity = coin_wallet.get("QUANTITY")

    # if we have coins already we dont buy more
    if quantity != 0:
        return

    print("Bought " + coin_name)

    close_price = float(msg["k"]["c"])

    while money >= close_price:
        money = money - close_price
        quantity += 1
        lastBuyPrices[coin_name] = close_price

    updateCollections(coin_name, "BUY", msg, quantity, quantity, money, trades_collection, wallet_collection)


def sell(coin_name: str, trading_bot_db: database.Database, msg):
    trades_collection: Collection = trading_bot_db.trades
    wallet_collection: Collection = trading_bot_db.wallet

    coin_wallet = wallet_collection.find_one({"SYMBOL": coin_name})

    money = 0
    quantity = 0
    # if coin is not in our wallet => create coin and give it 100k for trading
    if coin_wallet is None:
        wallet_collection.insert_one({"SYMBOL": coin_name, "QUANTITY": quantity, "MONEY": 100000})
        return
    else:
        money = coin_wallet.get("MONEY")
        quantity = coin_wallet.get("QUANTITY")

    close_price = float(msg["k"]["c"])
    last_buy_price = lastBuyPrices[coin_name]

    if (quantity > 0 and close_price > last_buy_price) or (quantity > 0 and (last_buy_price * 0.98) > close_price):
        print("SELL " + coin_name)

        if (last_buy_price * 0.98) > close_price:
            print("SOLD BECAUSE OF STOP LOSS")

        coins = quantity
        while coins != 0:
            money = money + close_price
            coins -= 1

        updateCollections(coin_name, "SELL", msg, quantity, 0, money, trades_collection, wallet_collection)


def updateCollections(coin_name, action, event, quantity, wallet_quantity, money, trades_collection, wallet_collection):
    # insert new trade
    trades_collection.insert_one({
        "SYMBOL": coin_name,
        "ACTION": action,
        "EVENT": event,
        "QUANTITY": quantity,
    })

    # update our wallet
    wallet_collection.update_one({
        'SYMBOL': coin_name
    }, {
        '$set': {
            'QUANTITY': wallet_quantity,
            'MONEY': money
        }
    }, upsert=False)


"""
{
  "e": "kline",     // Event type
  "E": 123456789,   // Event time
  "s": "BNBBTC",    // Symbol
  "k": {
    "t": 123400000, // Kline start time
    "T": 123460000, // Kline close time
    "s": "BNBBTC",  // Symbol
    "i": "1m",      // Interval
    "f": 100,       // First trade ID
    "L": 200,       // Last trade ID
    "o": "0.0010",  // Open price
    "c": "0.0020",  // Close price
    "h": "0.0025",  // High price
    "l": "0.0015",  // Low price
    "v": "1000",    // Base asset volume
    "n": 100,       // Number of trades
    "x": false,     // Is this kline closed?
    "q": "1.0000",  // Quote asset volume
    "V": "500",     // Taker buy base asset volume
    "Q": "0.500",   // Taker buy quote asset volume
    "B": "123456"   // Ignore
  }
}
"""
