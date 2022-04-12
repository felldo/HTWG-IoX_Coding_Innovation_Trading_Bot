from rest_framework.decorators import api_view
from rest_framework.response import Response
from binance import Client
import rest_framework.request
import os
import datetime

# ----------------#----------------#----------------#----------------#----------------#----------------
# MONGO DB
# ----------------#----------------#----------------#----------------#----------------#----------------
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
import urllib.parse

client = MongoClient('168.119.85.173:2379',
                     username='tb',
                     password=os.environ['MONGO_DB_PASSWORD'],
                     authSource='trading_bot',
                     authMechanism='SCRAM-SHA-256')

db = client.trading_bot
# Issue the serverStatus command and print the results
collection = db.test
# collection.insert_one({"hi":"jo"})

# for a in collection.find():
#    pprint.pprint(a)

# ----------------#----------------#----------------#----------------#----------------#----------------

isTrading = False  # Variable ob bot tradet oder nicht
startTime = datetime.datetime.now()  # runtime von bot
coinsToTrade = []

client = Client(api_key=os.environ['BINANCE_API_KEY'],
                api_secret=os.environ['BINANCE_SECRET'], testnet=True)
print(client.get_all_tickers())
print(client.get_my_trades(symbol="BTCBUSD"))

print(client.get_symbol_ticker(symbol="BTCBUSD"))
klinesData = client.get_historical_klines(
    "BTCBUSD", Client.KLINE_INTERVAL_1MINUTE, "2 minutes ago UTC")
print(klinesData)

"""
KLINES DATEN
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
  ]
]
"""


def changeTradingState(tradingState: bool, coinNames):
    isTrading = tradingState
    coinsToTrade = coinNames
    print("CHANGE TRADING STATE: " + isTrading)
    print(coinNames)


@api_view(['GET', 'POST'])
def get_bot_is_trading(request: rest_framework.request.Request):
    #
    # TODO: Change trading state and return something useful
    #

    if request.method == 'POST':
        changeTradingState(request.POST.get('tradingState'), request.POST.getlist('trading[]'))
    elif request.method == 'GET':
        print("GET BOT IS TRADING")

    data = {"trading": isTrading}
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_overview(request: rest_framework.request.Request):
    #
    # TODO: Implement this method correctly
    #
    data = {}
    data["startBalance"] = 100000
    data["currentBalance"] = 100000
    data["uptime"] = str(datetime.datetime.now() - startTime).split(".")[0]

    return Response(data=data, content_type="application/json")


### BINANCE API

@api_view(['GET'])
def get_klines_data(request: rest_framework.request.Request):
    data = client.get_historical_klines(
        request.query_params['name'], Client.KLINE_INTERVAL_30MINUTE, "30 days ago UTC")

    goodKlinesData = []
    for kline in data:
        manipulatedKline = [kline[0], float(kline[1]), float(
            kline[2]), float(kline[3]), float(kline[4]), float(kline[5])]
        goodKlinesData.append(manipulatedKline)
    return Response(data=goodKlinesData, content_type="application/json")


@api_view(['GET'])
def get_all_tickers(request: rest_framework.request.Request):
    data = client.get_all_tickers()
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_symbol_ticker(request: rest_framework.request.Request):
    print(request.user)
    print(request.query_params)
    data = client.get_symbol_ticker(symbol=request.query_params['name'])
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_symbol_info(request: rest_framework.request.Request):
    data = client.get_symbol_info(symbol=request.query_params['name'])
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_account_info(request: rest_framework.request.Request) -> Response:
    data = client.get_account()
    return Response(data=data, content_type="application/json")
