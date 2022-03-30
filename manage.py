#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IoX_Coding_Innovation.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()














#https://python-binance.readthedocs.io/en/latest/overview.html
#https://binance-docs.github.io/apidocs/#change-log

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
client = Client("key", "secret")

# get market depth
depth = client.get_order_book(symbol='BNBBTC')

print(client.get_symbol_info("BTCBUSD"))

print(client.get_symbol_ticker(symbol='BTCBUSD'))
print(client.get_symbol_ticker(symbol='DOGEBUSD'))

#for x in client.get_all_tickers():
#    print(x)
# place a test market buy order, to place an actual order use the create_order function
#order = client.create_test_order(
#    symbol='BNBBTC',
#    side=Client.SIDE_BUY,
#    type=Client.ORDER_TYPE_MARKET,
#    quantity=100)

# get all symbol prices
#prices = client.get_all_tickers()

# withdraw 100 ETH
# check docs for assumptions around withdrawals
#from binance.exceptions import BinanceAPIException
#try:
#    result = client.withdraw(
#        asset='ETH',
#        address='<eth_address>',
#        amount=100)
#except BinanceAPIException as e:
#    print(e)
#else:
#    print("Success")

# fetch list of withdrawals

#withdraws = client.get_withdraw_history()

# fetch list of ETH withdrawals
#eth_withdraws = client.get_withdraw_history(coin='ETH')

# get a deposit address for BTC
#address = client.get_deposit_address(coin='BTC')

# get historical kline data from any date range

# fetch 1 minute klines for the last day up until now
#klines = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
#print(klines)
# fetch 30 minute klines for the last month of 2017
#klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")
#print(klines)
# fetch weekly klines since it listed
#klines = client.get_historical_klines("NEOBTC", Client.KLINE_INTERVAL_1WEEK, "1 Jan, 2017")
#print(klines)

# socket manager using threads
twm = ThreadedWebsocketManager()
twm.start()

# depth cache manager using threads
dcm = ThreadedDepthCacheManager()
dcm.start()

def handle_socket_message(msg):
    print(f"message type: {msg['e']}")
    print(msg)

def handle_dcm_message(depth_cache):
    print(f"symbol {depth_cache.symbol}")
    print("top 5 bids")
    print(depth_cache.get_bids()[:5])
    print("top 5 asks")
    print(depth_cache.get_asks()[:5])
    print("last update time {}".format(depth_cache.update_time))

twm.start_kline_socket(callback=handle_socket_message, symbol='BNBBTC')

dcm.start_depth_cache(callback=handle_dcm_message, symbol='ETHBTC')

# replace with a current options symbol
options_symbol = 'BTC-210430-36000-C'
dcm.start_options_depth_cache(callback=handle_dcm_message, symbol=options_symbol)

# join the threaded managers to the main thread
twm.join()
dcm.join()








#def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
#    print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
