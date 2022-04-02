from rest_framework.decorators import api_view
from rest_framework.response import Response
from binance import Client
import rest_framework.request
import os

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


@api_view(['GET'])
def get_klines_data(request: rest_framework.request.Request):
    data = client.get_historical_klines(
        request.query_params['name'], Client.KLINE_INTERVAL_30MINUTE, "30 days ago UTC")

    goodKlinesData = []
    for kline in data:
        manipulatedKline = [kline[0], float(kline[1]), float(
            kline[2]), float(kline[3]), float(kline[4])]
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
