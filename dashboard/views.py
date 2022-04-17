from pymongo.collection import Collection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from binance import Client
import rest_framework.request, os, time, threading, datetime
import asyncio
import trading_bot.TradingBotWebsocket as tbsocket
from trading_bot.strategies.BollingerBand import BollingerBand
from trading_bot.strategies.MACD import MACD
import trading_bot.strategies.StrategyReturnType as stratType

import _thread as thread

# ----------------#----------------#----------------#----------------#----------------#----------------
# MONGO DB
# ----------------#----------------#----------------#----------------#----------------#----------------
from pymongo import MongoClient

mongoClient = MongoClient('better-tickets.de:2379',
                          username='tb',
                          password=os.environ['MONGO_DB_PASSWORD'],
                          authSource='trading_bot',
                          authMechanism='SCRAM-SHA-256')

db = mongoClient.trading_bot
# Issue the serverStatus command and print the results
collection = db.test
tradesCollection: Collection = db.trades

# collection.insert_one({"hi":"jo"})

# for a in collection.find():
#    pprint.pprint(a)

# ----------------#----------------#----------------#----------------#----------------#----------------

isTrading = False  # Variable ob bot tradet oder nicht
startTime = datetime.datetime.now()  # runtime von bot
coinsToTrade = []

binanceClient = Client(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_SECRET'], testnet=False)
# print(client.get_all_tickers())
# print(client.get_my_trades(symbol="BTCBUSD"))

# print(client.get_symbol_ticker(symbol="BTCBUSD"))
coinName = "BTCBUSD"
klinesData = binanceClient.get_historical_klines(coinName, Client.KLINE_INTERVAL_30MINUTE, "10 days ago UTC")
#print(klinesData)


#strat_bb = BollingerBand()
strat_macd = MACD()

cash = 500000
start_cash = cash
coins = 0
close_price = 0

stop_loss = 0.0

last_buy_price = 0


for x in klinesData:
    action = strat_macd.trade(x[0], float(x[4]))
    if action == stratType.StrategyReturnType.BUY:
        print("Bought")
        cash = cash - close_price
        coins += 1
        last_buy_price = close_price
    elif action == stratType.StrategyReturnType.SELL:
        print("Sold")
        cash = cash + close_price
        coins -= 1


"""
for x in klinesData:
    close_price = float(x[4])
    action = strat.trade(x[0], float(x[1]), close_price)
    if action == stratType.StrategyReturnType.BUY and coins == 0:

        # print("Bought")
        bought_price = 0
        while cash >= close_price:
            cash = cash - close_price
            coins += 1
            last_buy_price = close_price
        tradesCollection.insert_one({"symbol": coinName, "quantity": coins, "price": close_price, "total_price": close_price * coins, "action:": "BUY"})

    # sell if (strat tells to sell and you have bought and current_price > x) or the coin has dropped by 2 percent from the last buy price (last buy price * 0.98 > current_price)
    elif (action == stratType.StrategyReturnType.SELL and coins > 0 and close_price > last_buy_price) or (
            coins > 0 and (last_buy_price * 0.98) > close_price):
        # print("Sold")
        if (last_buy_price * 0.98) > close_price:
            print("SOLD BECAUSE OF STOP LOSS")
        tradesCollection.insert_one({"symbol": coinName, "quantity": coins, "price": close_price, "total_price": close_price * coins, "action:": "SELL"})
        while coins != 0:
            cash = cash + close_price
            coins -= 1
"""
print("--------------------------------------------------------------------------------------------------------")
print("PORSCHE CAYMAN S JUNGS KOMMT IN DIE GRUPPE: ", cash)
print("How much coins: ", coins)
print("coins worth: ", coins * last_buy_price)
print("EFFECTIVE TOTAL MONEY MADE:", cash + coins * close_price - start_cash)

print("-+-++-+--+-+-+-+-+-+-+-+--")
print("-+-++-+--+-+-+-+-+-+-+-+--")
print("-+-++-+--+-+-+-+-+-+-+-+--")
print("-+-++-+--+-+-+-+-+-+-+-+--")


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

"""
def doit(stop_event, arg):
    while not stop_event.wait(1):
        print ("working on %s" % arg)
    print("Stopping as you wish.")


def main():
    pill2kill = threading.Event()
    t = threading.Thread(target=doit, args=(pill2kill, "task"))
    t.start()
    time.sleep(5)
    pill2kill.set()
    t.join()
"""
trading_coins_pill = {}


def change_trading_state(trading_state: bool, coin_names, interval: str, strategy: str):
    global isTrading
    global trading_coins_pill
    print("CHANGE TRADING STATE: " + str(trading_state))
    x = True
    print("CHANGE TRADING STATE: " + str(x))
    if trading_state == True:
        print("TRADING STATE IS ", trading_state)
        isTrading = True
        pill2kill = threading.Event()
        trading_coins_pill = {}
        for coin in coin_names:
            if coin not in trading_coins_pill:
                # new_thread = threading.Thread(target=tbsocket.build_thread, args=(coin, pill2kill, strategy, binanceClient, interval,))
                # new_thread.start()
                print("TRADING STATE IS TRUE START THREAD")
                tid = thread.start_new_thread(tbsocket.build_thread, (coin, pill2kill, strategy, binanceClient, interval, tradesCollection,))
                trading_coins_pill[coin] = pill2kill
            else:
                print("22222222")
    else:
        isTrading = False
        print("TRADING COIN PILLS")
        print(trading_coins_pill)
        for coin in trading_coins_pill:
            trading_coins_pill[coin].set()
            print("SET TRADING COIND PILL")
            print(coin)

    print(coin_names)


@api_view(['GET', 'POST'])
def get_bot_is_trading(request: rest_framework.request.Request):
    global isTrading
    #
    # TODO: Change trading state and return something useful
    #

    if request.method == 'POST':
        change_trading_state(request.POST.get('tradingState') == "true", request.POST.getlist('trading[]'), request.POST.get('interval'),
                             request.POST.get('strategy'))
    elif request.method == 'GET':
        print("GET BOT IS TRADING")

    data = {"trading": isTrading, "coins": coinsToTrade}
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
    data = binanceClient.get_historical_klines(
        request.query_params['name'], Client.KLINE_INTERVAL_30MINUTE, "10 days ago UTC")

    goodKlinesData = []
    for kline in data:
        manipulatedKline = [kline[0], float(kline[1]), float(
            kline[2]), float(kline[3]), float(kline[4]), float(kline[5])]
        goodKlinesData.append(manipulatedKline)
    return Response(data=goodKlinesData, content_type="application/json")


@api_view(['GET'])
def get_all_tickers(request: rest_framework.request.Request):
    data = binanceClient.get_all_tickers()
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_symbol_ticker(request: rest_framework.request.Request):
    print(request.user)
    print(request.query_params)
    data = binanceClient.get_symbol_ticker(symbol=request.query_params['name'])
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_symbol_info(request: rest_framework.request.Request):
    data = binanceClient.get_symbol_info(symbol=request.query_params['name'])
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_account_info(request: rest_framework.request.Request) -> Response:
    data = binanceClient.get_account()
    return Response(data=data, content_type="application/json")

