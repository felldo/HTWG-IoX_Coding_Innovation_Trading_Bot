import os, time, datetime
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
import logging
import time
import os


from pymongo import MongoClient
from pymongo.collection import Collection

mongoClient = MongoClient('better-tickets.de:2379',
                          username='tb',
                          password=os.environ['MONGO_DB_PASSWORD'],
                          authSource='trading_bot',
                          authMechanism='SCRAM-SHA-256')

db = mongoClient.trading_bot
# Issue the serverStatus command and print the results
collection = db.test
tradesCollection: Collection = db.trades

wallet_collection: Collection = db.wallet
coin_wallet = wallet_collection.find_one({"SYMBOL": "BTCBUSD"})
print(coin_wallet)
print(coin_wallet.get("MONEY"))