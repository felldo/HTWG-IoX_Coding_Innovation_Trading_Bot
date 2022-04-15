# socket manager using threads
from binance import ThreadedWebsocketManager, ThreadedDepthCacheManager
import os
from binance.enums import *
from trading_bot.strategies.strategy1 import BollingerBand


symbol = 'BTCBUSD'

###twm = ThreadedWebsocketManager(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_SECRET'])
# start is required to initialise its internal loop
###twm.start()

###print("+++++++++++++++++++++++++1")
###def handle_socket_message(msg):
# print(f"message type: {msg['e']}")
###    print(msg)

###print("+++++++++++++++++++++++++2")
###twm.start_kline_socket(callback=handle_socket_message, symbol=symbol, interval=KLINE_INTERVAL_1MINUTE)

# multiple sockets can be started
# twm.start_depth_socket(callback=handle_socket_message, symbol=symbol, interval=WEBSOCKET_DEPTH_20)

# or a multiplex socket can be started like this
# see Binance docs for stream names
###streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
###twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

# streams = ['btcbusd@KLINE_' + KLINE_INTERVAL_1MINUTE]
# twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)
###print("+++++++++++++++++++++++++3")
###twm.join()
###print("+++++++++++++++++++++++++4")


import asyncio
from binance import AsyncClient, BinanceSocketManager
from datetime import datetime, timezone
from dateutil import tz

async def main():
    client = await AsyncClient.create(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_SECRET'])
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.kline_socket(symbol, interval=KLINE_INTERVAL_1MINUTE)
    strat = BollingerBand()
    # then start receiving messages
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            #strat.trade(res)
            event_time = datetime.fromtimestamp(res["E"] / 1000).astimezone(tz.gettz('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S')
            print(event_time, "\t", res)
            # Schauste nach wie viel wir halten von Coin

            strat.trade(res)

    await client.close_connection()




def start():
    print("+++++++++++++++++++0")
    loop = asyncio.get_event_loop()
    print("+++++++++++++++++++1")
    loop.run_until_complete(main())
    print("+++++++++++++++++++2")

    # loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

"""
from binance.client import Client
from binance.websockets import BinanceSocketManager
import _thread as thread
import time
import queue

api_key = ''
api_secret = ''
client = Client(api_key, api_secret)


def process_message(msg):
    if msg['s'] == 'ETHUSDT':
        print(f"{msg['s']} with delay, {time.strftime('%X')}")
        time.sleep(5)
        print('delay end')
    else:
        print(f"{msg['s']} {time.strftime('%X')}")


def build_thread(symbol):
    print('start thread', symbol)
    q = queue.Queue()
    bm = BinanceSocketManager(client, user_timeout=60)
    conn_key = bm.start_kline_socket(symbol, q.put, '1h')
    bm.start()
    while (True):
        msg = q.get()
        process_message(msg)


tid = thread.start_new_thread(build_thread, ('ETHUSDT',))
thread.start_new_thread(build_thread, ('BNBUSDT',))


class CountdownTask:

    def __init__(self):
        self._running = True


def terminate(self):
    self._running = False


def run(self, n):
    while self._running and n > 0:
        print('T-minus', n)
        n -= 1
        time.sleep(5)


c = CountdownTask()
t = Thread(target=c.run, args=(10,))
t.start()
...
# Signal termination
c.terminate()

# Wait for actual termination (if needed)
t.join()
"""