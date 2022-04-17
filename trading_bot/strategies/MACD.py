# Andere strategie
import pprint
from collections import deque
from pathlib import Path

import pandas as pd
import numpy as np
from pandas import DataFrame, Series

from trading_bot.strategies.StrategyReturnType import *
from datetime import datetime
from dateutil import tz


class MACD:
    prev_row: Series
    # Set intersection to 0 at the start
    intersection = 0
    old_time = 0
    # Most Popular Combination of fast/slow length and signal values
    fast_length = 12
    slow_length = 26
    signal_line = 9
    #                   Epoch Time,  Open_Price to Epoch Time, Close_Price, Bought/Sold Flag
    close_price_list_pd: DataFrame = pd.DataFrame(columns=['open_time', 'close_price', 'bought/sold', 'intersection'])

    # Returns current close_price_list
    def get_data(self):
        return self.close_price_list_pd

    # Adds new row of Data to our List
    def add_kline_to_list(self, open_time, close_price):
        # Query, so it doesn't add the same Data with the same Opentime
        if open_time > self.old_time:
            new = {'open_time': [open_time], 'close_price': [close_price], 'bought/sold': [0], 'intersection': [0]}
            new_row = pd.DataFrame(data=new)
            self.close_price_list_pd = pd.concat([self.close_price_list_pd, new_row], ignore_index=True, join='inner')
            self.old_time = open_time
        # print(self.close_price_list_pd)

    # Calculates the Moving Average Convergence/Divergence (MACD)
    def get_macd(self, close_price):
        price = pd.DataFrame(data=close_price)
        # Alpha = 2 / (span + 1)
        # Exp1, Alpha = 2 / (12 + 1) = 0,154
        exp1 = price['close_price'].ewm(span=self.fast_length, adjust=False).mean()
        # Exp1, Alpha = 2 / (26 + 1) = 0,074
        exp2 = price['close_price'].ewm(span=self.slow_length, adjust=False).mean()
        # Set Frames for Panda
        open_time = pd.DataFrame(data=self.close_price_list_pd['open_time']).rename(columns={0: 'open_time'})
        # open_time = self.close_price_list_pd['open_time']
        bought_sold = pd.DataFrame(data=self.close_price_list_pd['bought/sold']).rename(columns={0: 'bought/sold'})
        intersection = pd.DataFrame(data=self.close_price_list_pd['intersection']).rename(columns={0: 'intersection'})
        macd = pd.DataFrame(exp1 - exp2).rename(columns={'close_price': 'macd'})
        signal = pd.DataFrame(macd.ewm(span=self.signal_line, adjust=False).mean()).rename(columns={'macd': 'signal'})
        hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns={0: 'hist'})
        # Connect Frame to new Panda DataFrame
        frames = [open_time, macd, signal, hist, bought_sold, intersection]
        df = pd.concat(frames, join='inner', axis=1, ignore_index=True)
        # print(df)
        return df

    # Implements the MACD trading strategyx
    def trade(self, open_time, close_price):
        # Adds new Fetch of Information to the List
        self.add_kline_to_list(open_time, close_price)
        # Get Data of Moving Average Convergence/Divergence
        data = self.get_macd(self.get_data())
        # print(type(data))
        # print("+++++++++++++++++++++++++++++++++++++++++++++")
        # for index, (_,row) in enumerate(data.iterrows()):
        # print(index)
        #print("NEW ITERATION")

        for index, (_, row) in enumerate(data.iterrows()):
            # Sell if MACD > Singal and intersection
            # print("DATA", data)
            #print("INDEX: ", index)
            # print("UNKNOWN: ",_)
            # print(data.loc[i]['macd'])
            # print(i, row)
            # print(row)
            # print("++++++++++++++++++++++")
            # print(self.close_price_list_pd['bought/sold'])
            # ("--------------------")
            # print(self.close_price_list_pd['bought/sold'][index])

            if row[1] > row[2]:
                # nicht gekauft und noch nicht geschnitten
                if row[4] == 0 and row[5] == 0 and self.prev_row[5] != 2:
                    # wenn der vorherige eine intersection war dann soll die intersection auf zwei gesetzt werden
                    if self.prev_row[5] == 1:
                        self.close_price_list_pd.loc[index, 'bought/sold'] = 0
                        self.close_price_list_pd.loc[index, 'intersection'] = 2
                    else:
                        self.close_price_list_pd.loc[index, 'bought/sold'] = 1
                        self.close_price_list_pd.loc[index, 'intersection'] = 1
                        print("Bought at {}".format(open_time))
                        return StrategyReturnType.BUY
                else:
                    self.close_price_list_pd.loc[index, 'intersection'] = 2
                    # Marks that the Two Lines of MACD and Signal had an Intersection
                    #self.intersection = 1
                    # Append a Bought Flag

                    #if self.prev_row[4] != 0:
                    #    self.close_price_list_pd.loc[index, 'intersection'] = 1
            # Sell if Singal > MACD and intersection
            elif row[2] > row[1]:
                if row[4] == 0 and self.prev_row[5] == 2:
                    # Marks that the Two Lines of MACD and Signal had an Intersection
                    #self.intersection = -1
                    # Append a Sold Flag
                    self.close_price_list_pd.loc[index, 'intersection'] = 1
                    self.close_price_list_pd.loc[index, 'bought/sold'] = 2
                    print("Sold at {}".format(open_time))
                    return StrategyReturnType.SELL
            self.prev_row = row
        #f = open("test.txt", "w")
        #f.write(data.to_string())
        #f.close()
        print(data.to_string())

        return StrategyReturnType.HOLD


if __name__ == '__main__':
    macd = MACD()
    # macd.add_kline_to_list(10000, 100)
    # macd.get_data()
    open_prices = pd.DataFrame(data=macd.close_price_list_pd)
    macd.get_macd(open_prices['open_price'])
