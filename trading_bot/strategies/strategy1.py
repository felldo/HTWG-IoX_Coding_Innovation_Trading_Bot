# Bollinger Bands strategie
from collections import deque

import numpy as np
from trading_bot.strategies.StrategyReturnType import *
from datetime import datetime
from dateutil import tz


class BollingerBand:
    # 1. Open Price von Kline anschauen
    # 2. Das ganze in eine Deque speicher
    # 3. Sobald deque X Werte hat den ersten in der Liste rausschmeißen und den nächsten hinzufügen
    # 4. Jedesmal bei diesem Schritt wird die Berechnung für Upper und Lower Band berechnet

    lastTwenty = deque([])
    old_time = 0

    # Appends Element to end of Deque until it has a length of 20
    # If length of 20, Pop the first element and append the new one to the end
    def maintanDeque(self, element, time):
        # Wenn gleiche data["k"]["t"] dann nicht hinzufügen
        if time > self.old_time:
            if len(self.lastTwenty) >= 20:
                self.lastTwenty.popleft()
            self.lastTwenty.append(element)
            self.old_time = time

    # mean = getMeanOfDeque
    # nstd = Wie viel die Standardabweichung aussagt
    def bollingerBand(self, mean, nstd):
        std = np.std(self.lastTwenty)
        upper_band = mean + std * nstd
        lower_band = mean - std * nstd
        return upper_band, lower_band

    def trade(self, open_time, open_price, closed_price):
        # Get OpenPrice
        self.maintanDeque(open_price, open_time)

        epochtime = open_time / 1000
        to_zone = tz.gettz('Europe/Berlin')
        current_time = datetime.fromtimestamp(epochtime).astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')

        if len(self.lastTwenty) == 20:
            # Average of the last twenty calls we did
            mean = np.mean(self.lastTwenty)
            # Get the upper and lower band of the BollingerBand Strategie
            upper_band, lower_band = self.bollingerBand(mean, 3)
            if lower_band > closed_price:
                return StrategyReturnType.BUY
            elif upper_band < closed_price:
                return StrategyReturnType.SELL
        return StrategyReturnType.HOLD
