# Andere strategie
import pprint
from collections import deque
from pathlib import Path

import pandas as pd
import numpy as np
from trading_bot.strategies.StrategyReturnType import *
from datetime import datetime
from dateutil import tz

class MACD:
    old_time = 0
    # Most Popular Combination of fast/slow length and signal values
    fast_length = 12
    slow_length = 26
    signal_line = 9
    #                   Epoch Time,  Open_Price to Epoch Time, Close_Price, Bought/Sold Flag
    close_price_list = {'open_time': [], 'close_price': [], 'bought/sold': []}
    """
    dataaa = {
        "open_time" : 10,
        "close_price": 10,
        "bought/sold": 10,
    }
    close_price_list = []
    close_price_list.append(dataaa)
    """

    # Returns current close_price_list
    def get_data(self):
        dataframe = pd.DataFrame(data=self.close_price_list)
        return dataframe

    # Adds new row of Data to our List
    def add_kline_to_list(self, open_time, close_price):
        # Query, so it doesn't add the same Data with the same Opentime
        if open_time > self.old_time:
            self.close_price_list['open_time'].append(open_time)
            self.close_price_list['close_price'].append(close_price)
            self.close_price_list['bought/sold'].append(0)
            self.old_time = open_time
        #print(self.close_price_list)

    # Calculates the Moving Average Convergence/Divergence (MACD)
    def get_macd(self, close_price):
        price = pd.DataFrame(data=close_price)
        # Alpha = 2 / (span + 1)
        # Exp1, Alpha = 2 / (12 + 1) = 0,154
        exp1 = price.ewm(span=self.fast_length, adjust=False).mean()
        # Exp1, Alpha = 2 / (26 + 1) = 0,074
        exp2 = price.ewm(span=self.slow_length, adjust=False).mean()
        # Set Frames for Panda
        open_time = pd.DataFrame(data=self.close_price_list['open_time']).rename(columns={0: 'open_time'})
        bought_sold = pd.DataFrame(data=self.close_price_list['bought/sold']).rename(columns={0: 'bought/sold'})
        macd = pd.DataFrame(exp1 - exp2).rename(columns={'close_price': 'macd'})
        signal = pd.DataFrame(macd.ewm(span=self.signal_line, adjust=False).mean()).rename(columns={'macd': 'signal'})
        hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns={0: 'hist'})

        # Connect Frame to new Panda DataFrame
        frames = [open_time, macd, signal, hist, bought_sold]
        df = pd.concat(frames, join='inner', axis=1)
        #print(df)
        return df

    # Implements the MACD trading strategyx
    def trade(self, open_time, close_price):
        # Adds new Fetch of Information to the List
        self.add_kline_to_list(open_time, close_price)
        # Get Data of Moving Average Convergence/Divergence
        data = self.get_macd(self.get_data())
        #print(type(data))
        # Set intersection to 0 at the start
        #print("+++++++++++++++++++++++++++++++++++++++++++++")


        intersection = 0
        for i in data.iterrows():
            """
            if i == len(data) - 1:
                filepath = Path('C:/Users/dfell/PycharmProjects/IoX_Coding_Innovation/trading_bot/strategies/out.csv')
                filepath.parent.mkdir(parents=True, exist_ok=True)
                data.to_csv(filepath)
                pprint.pprint(data.to_string())
                #print(data.shape[0])
                f = open("test.txt", "w")
                f.write(data.to_string())
                f.close()
                #print(self.close_price_list)
            """
            # Sell if MACD > Singal and intersection
            if data['macd'][i] > data['signal'][i]:
                if intersection != 1 and self.close_price_list['bought/sold'][i] != 1:
                    # Marks that the Two Lines of MACD and Signal had an Intersection
                    intersection = 1
                    # Append a Bought Flag
                    self.close_price_list['bought/sold'][i].append(1)
                    print("bought")
                    return StrategyReturnType.BUY
                else:
                    # Append a did nothing Flag
                    self.close_price_list['bought/sold'][i].append(0)
                    print("do nothing buyyy")
            # Sell if Singal > MACD and intersection
            elif data['signal'][i] > data['macd'][i]:
                if intersection == 1 and self.close_price_list['bought/sold'][i] != 2:
                    # Marks that the Two Lines of MACD and Signal had an Intersection
                    intersection = -1
                    # Append a Sold Flag
                    self.close_price_list['bought/sold'][i].append(2)
                    print("sold")
                    return StrategyReturnType.SELL
                else:
                    # Append a did nothing Flag
                    self.close_price_list['bought/sold'][i].append(0)
                    print("do nothing solddd")
            else:
                return StrategyReturnType.HOLD



if __name__ == '__main__':
    macd = MACD()
    #macd.add_kline_to_list(10000, 100)
    #macd.get_data()
    open_prices = pd.DataFrame(data=macd.close_price_list)
    macd.get_macd(open_prices['open_price'])

