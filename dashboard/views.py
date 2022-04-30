from rest_framework.decorators import api_view
from rest_framework.response import Response
#from binance import Client
from python_binance import Client
import rest_framework.request, os, threading, datetime
import trading_bot.TradingBotWebsocket as tbsocket
from pymongo import MongoClient
from pymongo.collection import Collection
import _thread as thread
import json

# ----------------#----------------#----------------#----------------#----------------#----------------
# MONGO DB
# ----------------#----------------#----------------#----------------#----------------#----------------
mongoClient = MongoClient('better-tickets.de:2379',
                          username='tb',
                          password=os.environ['MONGO_DB_PASSWORD'],
                          authSource='trading_bot',
                          authMechanism='SCRAM-SHA-256')

db = mongoClient.trading_bot
# ----------------#----------------#----------------#----------------#----------------#----------------

isTrading = False  # Variable ob bot tradet oder nicht
startTime = datetime.datetime.now()  # runtime von bot
coinsToTrade = []

binanceClient = Client(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_SECRET'], testnet=False)

print("-+-++-+--+-+-+-+-+-+-+-+--")
print("-+-++-+--+-+-+-+-+-+-+-+--")
print("-+-++-+--+-+-+-+-+-+-+-+--")
print("-+-++-+--+-+-+-+-+-+-+-+--")

trading_coins_pill = {}

def change_trading_state(trading_state: bool, coin_names, interval: str, strategy: str):
    global isTrading
    global trading_coins_pill
    global coinsToTrade

    if trading_state == True:
        isTrading = True
        pill2kill = threading.Event()
        trading_coins_pill = {}
        coinsToTrade = coin_names
        for coin in coin_names:
            if coin not in trading_coins_pill:
                tid = thread.start_new_thread(tbsocket.build_thread, (coin, pill2kill, strategy, binanceClient, interval, db,))
                trading_coins_pill[coin] = pill2kill
    else:
        coinsToTrade = []
        isTrading = False
        for coin in trading_coins_pill:
            trading_coins_pill[coin].set()

    print(coin_names)


@api_view(['GET', 'POST'])
def get_bot_is_trading(request: rest_framework.request.Request):
    global isTrading

    if request.method == 'POST':
        change_trading_state(request.POST.get('tradingState') == "true", request.POST.getlist('trading[]'), request.POST.get('interval'),
                             request.POST.get('strategy'))
    elif request.method == 'GET':
        print("GET BOT IS TRADING")

    data = {"trading": isTrading, "coins": coinsToTrade}
    return Response(data=data, content_type="application/json")


@api_view(['GET'])
def get_overview(request: rest_framework.request.Request):
    coinsWithPrice = binanceClient.get_all_tickers()

    wallet_collection: Collection = db.wallet
    wallet = wallet_collection.find({},{"_id": 0})

    list_cur = list(wallet)

    for index, x in enumerate(list_cur):
        symbol = x['SYMBOL']
        quantity = x['QUANTITY']
        money = x['MONEY']
        price = [d for d in coinsWithPrice if d['symbol'] in symbol][0]['price']

        list_cur[index]['NET'] = float(price) * float(quantity) + float(money)

    data = {"wallet": list_cur, "uptime": str(datetime.datetime.now() - startTime).split(".")[0]}
    resp = {'Access-Control-Allow-Origin': '*'}
    return Response(data=data, content_type="application/json", headers=resp)


### BINANCE API
@api_view(['GET'])
def get_klines_data(request: rest_framework.request.Request):
    print("PARAMS")
    print(request.query_params)

    interval = request.query_params['interval']
    symbol = request.query_params['symbol']
    startDate = int(request.query_params['startDate'])
    endDate = int(request.query_params['endDate'])

    klineData = binanceClient.get_historical_klines(symbol, interval, startDate, endDate)

    goodKlinesData = []
    for kline in klineData:
        manipulatedKline = [kline[0], float(kline[1]), float(
            kline[2]), float(kline[3]), float(kline[4]), float(kline[5])]
        goodKlinesData.append(manipulatedKline)

    trades_collection: Collection = db.trades
    markers = trades_collection.find(
        {
            "SYMBOL": symbol,
            "$and": [
                {"EVENT.E": {"$lte": endDate}},
                {"EVENT.E": {"$gte": startDate}}
            ]
        },
        {"_id": 0}
    )

    list_cur = list(markers)
    data = {"klineData": goodKlinesData, "klineMarker": list_cur}

    return Response(data=data, content_type="application/json")


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

