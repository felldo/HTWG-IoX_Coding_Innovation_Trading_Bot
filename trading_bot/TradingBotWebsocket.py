# socket manager using threads
from binance import ThreadedWebsocketManager, ThreadedDepthCacheManager
import os

from datetime import datetime, timezone
from dateutil import tz
from binance.enums import *
from trading_bot.strategies.BollingerBand import BollingerBand


# symbol = 'BTCBUSD'

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


def build_thread(symbol, stop_event):
    print('start thread', symbol)
    twm = ThreadedWebsocketManager(api_key=os.environ['BINANCE_API_KEY'], api_secret=os.environ['BINANCE_SECRET'])
    # start is required to initialise its internal loop
    twm.start()
    algorithm = BollingerBand()

    def handle_socket_message(msg):
        if stop_event.is_set():
            print("TRYING TO STOP")
            twm.stop()
            return
        print("MESSAGE RECEIVED")
        event_time = datetime.fromtimestamp(msg["E"] / 1000).astimezone(tz.gettz('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S')
        #print(event_time, "\t", msg)
        algorithm.trade(msg["k"]["t"], float(msg["k"]["o"]), float(msg["k"]["c"]))
        # print(f"message type: {msg['e']}")
        # print(msg)

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    print("THREAD JOIN")
    twm.join()
