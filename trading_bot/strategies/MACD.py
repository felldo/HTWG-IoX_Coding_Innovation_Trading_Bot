# Andere strategie
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from trading_bot.strategies.StrategyReturnType import *


class MACD:
    # Create prev_row variable for saving the row of the last iteration
    prev_row: Series
    # Set intersection to 0 at the start
    intersection = 0
    # Set old time to 0 at the start
    old_time = 0
    # Most Popular Combination of fast/slow length and signal values
    fast_length = 12
    slow_length = 26
    signal_line = 9
    #                                                       Open_Time , Close_Price, Bought/Sold Flag, Intersection Flag
    close_price_list_pd: DataFrame = pd.DataFrame(columns=['open_time', 'close_price', 'bought/sold', 'intersection'])

    # Returns current close_price_list
    def get_data(self):
        return self.close_price_list_pd

    # Adds new row of Data to our List
    def add_kline_to_list(self, open_time, close_price):
        # Query, so it doesn't add the same Data with the same open time
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
        # Set Frames for new DataFrame
        macd = pd.DataFrame(exp1 - exp2).rename(columns={'close_price': 'macd'})
        open_time = pd.DataFrame(data=self.close_price_list_pd['open_time']).rename(columns={0: 'open_time'})
        # open_time = self.close_price_list_pd['open_time']
        bought_sold = pd.DataFrame(data=self.close_price_list_pd['bought/sold']).rename(columns={0: 'bought/sold'})
        intersection = pd.DataFrame(data=self.close_price_list_pd['intersection']).rename(columns={0: 'intersection'})
        signal = pd.DataFrame(macd.ewm(span=self.signal_line, adjust=False).mean()).rename(columns={'macd': 'signal'})
        hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns={0: 'hist'})
        # Connect Frames to new Panda DataFrame
        frames = [open_time, macd, signal, hist, bought_sold, intersection]
        full_DataFrame = pd.concat(frames, join='inner', axis=1, ignore_index=True)
        return full_DataFrame

    # Implements the MACD trading strategy
    def trade(self, open_time, close_price):
        # Adds new Fetch of Information to the List
        self.add_kline_to_list(open_time, close_price)
        # Get Data of Moving Average Convergence/Divergence
        data = self.get_macd(self.get_data())
        for index, (_, row) in enumerate(data.iterrows()):
            # Buy if MACD > signal and intersection
            if row[1] > row[2]:
                # If it isn't bought and isn't an intersection and the previous row is no intersection go on
                if row[4] == 0 and row[5] == 0 and self.prev_row[5] != 2:
                    # If the prev row is the intersection point
                    if self.prev_row[5] == 1:
                        # Then the new one couldn't be bought and the intersection Flag is set to 2 because it
                        # is between two intersection
                        self.close_price_list_pd.loc[index, 'bought/sold'] = 0
                        self.close_price_list_pd.loc[index, 'intersection'] = 2
                    # If it's not an intersection point
                    else:
                        # Then you set the Bought and intersection Flag to 1 and return Buy Signal for the Bot
                        self.close_price_list_pd.loc[index, 'bought/sold'] = 1
                        self.close_price_list_pd.loc[index, 'intersection'] = 1
                        return StrategyReturnType.BUY
                # Else we are just between two intersections, so set the Flag to 2
                else:
                    self.close_price_list_pd.loc[index, 'intersection'] = 2
            # Else Sell if signal > MACD
            elif row[2] > row[1]:
                # If the current isn't bought and the prev row has an intersection Flag set to 2
                if row[4] == 0 and self.prev_row[5] == 2:
                    # Append a Sold Flag and that it is a intersection and return Sell Signal for the Bot
                    self.close_price_list_pd.loc[index, 'intersection'] = 1
                    self.close_price_list_pd.loc[index, 'bought/sold'] = 2
                    return StrategyReturnType.SELL
            # After one full iteration set the current Row to the Previous_row so we can check both Rows
            # in the next iteration
            self.prev_row = row
        # If you can't sell or buy you just Hold
        return StrategyReturnType.HOLD
