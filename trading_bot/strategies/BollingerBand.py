# Bollinger Bands strategie
from collections import deque

import numpy as np
from trading_bot.strategies.StrategyReturnType import *


class BollingerBand:
    # Empty deque to start with
    lastTwenty = deque([])
    # Set old_time to 0 at the beginning
    old_time = 0
    #
    # Appends Element to end of Deque until it has a length of 20
    # If length of 20, Pop the first element and append the new one to the end
    def maintan_deque(self, open_price, open_time):
        # If same data["k"]["t"] then don't add
        if open_time > self.old_time:
            if len(self.lastTwenty) >= 20:
                self.lastTwenty.popleft()
            self.lastTwenty.append(open_price)
            self.old_time = open_time

    # mean = getMeanOfDeque
    # nstd = Weight of Standard Deviation
    def bollinger_band(self, mean, nstd):
        std = np.std(self.lastTwenty)
        upper_band = mean + std * nstd
        lower_band = mean - std * nstd
        return upper_band, lower_band

    # Implements the Bollinger_Band trading strategy
    def trade(self, open_time, open_price, closed_price):
        # Get OpenPrice
        self.maintan_deque(open_price, open_time)
        # print(self.lastTwenty)
        if len(self.lastTwenty) == 20:
            # Average of the last twenty calls we did
            mean = np.mean(self.lastTwenty)
            # Get the upper and lower band of the BollingerBand strategy
            upper_band, lower_band = self.bollinger_band(mean, 3)
            if lower_band > closed_price:
                # Return Buy Flag
                return StrategyReturnType.BUY
            elif upper_band < closed_price:
                # Return Sell Flag
                return StrategyReturnType.SELL
        return StrategyReturnType.HOLD
