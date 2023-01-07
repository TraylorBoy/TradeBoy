"""Automated Crypto Trader"""

import datetime

from client.proxy import Proxy
from helpers.info import Info
from helpers.stats import Stats
from helpers.calc import tp, sl
from time import sleep

# TODO: Spot engine - Wait for more investment opportunities
# TODO: exit engine
# TODO: Create unified symbol for both spot and future
# TODO: Fix docstrings
# TODO: GUI
# TODO: Figure out how to not double init (in strategy and to use engine) - Make public exchange client (X)
# TODO: Add CoinbaseBoy
# TODO: Add more indicators - Test more strategies (will have to work on CandleBoy as well) (mesa and stoch indies)
# TODO: Add exit condition to future engine
# TODO: Make strategy repo
# TODO: Add current profit while in position
# TODO: Have log go to mobile phone
# TODO: CandleBoy - Work on swing low/high algo
# TODO: Add change_account for future if exchange allows sub accounts
# TODO: Add avg time in position


class Engine:
    RATE = 20  # Sleep time

    def __init__(self, exchange, silent=True):
        try:
            self._proxy = Proxy(exchange, silent)
            self._info = Info(self._proxy)
            self._stats = Stats(self._proxy)
            self._silent = silent
        except Exception as e:
            self._log(e)
            raise Exception(e)

# ------------------------------- Class Methods ------------------------------ #

    def _sync(self):
        """Waits until the new minute starts"""
        t = datetime.datetime.utcnow()
        x = 60 - (t.second + t.microsecond/1000000.0)
        sleep(x)

    def _fill(self, type, entry_price, symbol, tp_percent, sl_percent, side, amount):
        """Wait for order to be filled (only works for limit order types)"""
        if type == 'limit':
            entry = entry_price
            while not self._proxy.in_position(symbol):
                self._log('Waiting for order to be filled')
                price = self._proxy.price(symbol)
                if price > entry or price < entry:
                    tp = tp(tp_percent, side, price)
                    sl = sl(sl_percent, side, price)
                    self._proxy.reopen_position(
                        side, symbol, type, amount, price, sl, tp)
                sleep(self.RATE)

    def _wait(self, symbol):
        """Wait for tp/sl target to hit"""
        while self._proxy.in_position(symbol):
            self._log('In position')
            self._log(self._info)
            sleep(self.RATE)

    def _future_engine(self):
        """Initiates trades within the future market"""
        try:
            # Unpack data
            side = self._info.data['side']
            symbol = self._info.data['symbol']
            amount = self._info.data['amount']
            sl_percent = self._info.data['sl']
            tp_percent = self._info.data['tp']
            type = self._info.data['type']

            # Calculate tp and sl price targets
            price = self._proxy.price(symbol)
            tp = tp(tp_percent, side, price)
            sl = sl(sl_percent, side, price)
            self._info.update_targets(tp, sl)

            # Initiate trade
            self._proxy.open_position(
                side, symbol, type, amount, price, sl, tp)

            # Make sure limit order gets filled
            self._fill(type, price, symbol, tp_percent,
                       sl_percent, side, amount)

            # Wait for tp/sl target to hit
            self._wait(symbol)

            # Calculate profit, add to trades
            self._stats.update()
        except Exception as e:
            self._log(e)
            raise Exception('Failed during future engine execution')
        self._log('Position closed')

    def _entry_engine(self, strategy):
        """Finds an entry

        strategy (Class Object) - Separate module created by client (see docs)
        """
        try:
            while not strategy.entry():
                self._log('Looking for entry')
                self._log(self._stats)
                sleep(self.RATE)
        except Exception as e:
            self._log(e)
            raise Exception('Failed during entry engine execution')
        self._log('Entry found')

# ------------------------------ Client Methods ------------------------------ #

    def _spot_engine(self):
        """Initiates trades within the spot market"""
        pass

    def run(self, Strategy, limit=100):
        """Runs the strategy

        Strategy (Class) - Separate module created by client (see docs)
        limit (Int) - How many times the engine should run strategy (defaults at 100)
        """
        try:
            strategy = Strategy()
            # Initiate engine
            while self._stats.data['trades'] <= limit:
                # Wait for new minute
                self._log('Syncing to current time')
                self._sync()
                # Find entry
                self._entry_engine(strategy)
                # Entry found
                # Collect strategy data
                self._info.collect(strategy)
                # Run market engine
                code = self._info.data['code']
                if code == 'future':
                    self._future_engine()
        except Exception as e:
            self._log(e)
            raise Exception('Failed during main engine execution')
