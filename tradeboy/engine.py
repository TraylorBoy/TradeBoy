"""Automated Crypto Trader"""

import os
import datetime

from time import sleep
from candleboy import CandleBoy
from phemexboy import PhemexBoy
from dotenv import load_dotenv
load_dotenv()

# TODO: Refactor - Seperate classes (X)
# TODO: Error handling - CODES?
# TODO: Spot engine - Wait for more investment opportunities
# TODO: exit engine
# TODO: Create unified symbol for both spot and future
# TODO: Fix docstrings
# TODO: GUI
# TODO: Figure out how to not double init (in strategy and to use engine) - Make public exchange client
# TODO: Add CoinbaseBoy
# TODO: Add more indicators - Test more strategies (will have to work on CandleBoy as well)
# TODO: Add exit condition to future engine
# TODO: Make strategy repo
# TODO: Add current profit while in position
# TODO: Have log go to mobile phone
# TODO: CandleBoy - Work on swing low/high algo
# TODO: Add SLEEP_TIME variable
# TODO: Add change_account for future if exchange allows sub accounts
# TODO: Add avg time in position
# TODO: Fix tests - test EVERY METHOD


class TradeBoy:
    CODES = ['spot', 'future', 'buy', 'sell', 'long', 'short']

    def __init__(self, exchange, silent=True):
        # Setup class properties
        self.exchange = exchange
        self.silent = silent
        self.stats = {'wins': 0, 'losses': 0, 'profit': 0, 'trades': 0}
        self.info = {}

# ------------------------------- Class Methods ------------------------------ #

    def _log_trade_info(self):
        """Outputs trade information"""
        self._log_info()
        self._log_stats()

    def _log_info(self):
        """Output info"""
        side = self.info['side']
        symbol = self.info['symbol']
        amount = self.info['amount']
        sl = self.info['sl']
        tp = self.info['tp']
        code = self.info['code']
        entry = round(self.info['entry'], 2)

        price = round(self.price(symbol), 2)
        balance = round(self.balance('USD', code), 2)

        self._log(
            f'\nTrade Information\n----------\nSide: {side}\nBalance: ${balance}\nPrice: ${price}\nEntry: ${entry}\nTP: ${tp}\nSL: ${sl}\nAmount: {amount}')

    def _log_stats(self):
        """Displays stats to output"""
        wins = self.stats['wins']
        losses = self.stats['losses']
        profit = round(self.stats['profit'], 2)
        trades = self.stats['trades']

        self._log(
            f'\nStats\n-------\nWins: {wins}\nLosses: {losses}\nProfit: {profit} (USD)\nTrades: {trades}\n')

    def _open_position(self, side, symbol, type, amount, price, sl, tp):
        """Opens a position within the future market"""
        self._log('\nOpening a position\n')
        if side == 'long':
            # Open long position
            self._client.long(symbol, type, amount, price, sl, tp)

        elif side == 'short':
            # Open short position
            self._client.short(symbol, type, amount, price, sl, tp)

    def _update_stats(self):
        """Returns current profit or loss"""
        code = self.info['code']
        bal_before = round(self.info['balance'], 2)
        bal = round(self.balance('USD', code), 2)

        self._log('\nCalculating profit\n')
        self._log(f'\nBAL_BEFORE: {bal_before}\nBAL_AFTER: {bal}\n')
        if bal_before < bal:
            self.stats['wins'] += 1
        if bal_before > bal:
            self.stats['losses'] += 1
        self.stats['profit'] += round(bal - bal_before, 2)

    def _profit_percent(self, percent, side, price):
        """Calculates take profit price based off of percentage from current price

        symbol (String) - Symbol to calculate profit price for (ex. BTC/USD:USD)
        percent (Integer) - Percent to calculate profit price
        side (String) - What side of the trade you are on (ex. long, short, buy, sell)
        price (Double) - Current price
        """
        if side == 'long':
            return round(price + (price * (percent / 100)), 2)
        if side == 'short':
            return round(price - (price * (percent / 100)), 2)

    def _loss_percent(self, percent, side, price):
        """Calculates stop loss price based off of percentage from current price

        symbol (String) - Symbol to calculate stop loss price for (ex. BTC/USD:USD)
        percent (Integer) - Percent to calculate stop loss price
        side (String) - What side of the trade you are on (ex. long, short, buy, sell)
        price (Double) - Current price
        """
        if side == 'long':
            return round(price - (price * (percent / 100)), 2)
        if side == 'short':
            return round(price + (price * (percent / 100)), 2)

    def _close_position(self):
        """Checks if tp or sl has triggered and updates stats"""
        self._log('\nUpdating stats\n')
        self._update_stats()
        self._log(f'\nStats Updated\nProfit: {self.stats["profit"]}\n')

    def _wait_to_start(self):
        """Waits until the new minute starts"""
        t = datetime.datetime.utcnow()
        x = 60 - (t.second + t.microsecond/1000000.0)
        sleep(x)

    def _reopen(self, side, symbol, type, amount, price, sl, tp):
        """Cancel pending order and reopen position"""
        # Cancel order
        self._client.cancel_all(symbol)
        # Reopen position
        self._open_position(side, symbol, type, amount, price, sl, tp)

    def _future_engine(self):
        """Initiates trades within the future market"""
        side = self.info['side']
        symbol = self.info['symbol']
        amount = self.info['amount']
        sl_percent = self.info['sl']
        tp_percent = self.info['tp']
        type = self.info['type']

        # Calculate params
        self._log('\nCalculating params\n')
        price = self.price(symbol)
        tp = self._profit_percent(tp_percent, side, price)
        sl = self._loss_percent(sl_percent, side, price)
        self._log(
            f'\nParams Calculated\n-------\nTP: {tp}\nSL: {sl}\nPrice: {price}\n')

        # Update info
        self.info['sl'] = sl
        self.info['tp'] = tp

        self._log('\nPlacing order\n')
        self._open_position(side, symbol, type, amount, price, sl, tp)

        if type == 'market':
            self.info['entry'] = self.price(symbol)

        if type == 'limit':
            self.info['entry'] = price

        while not self.in_position(symbol):
            self._log('\nWaiting for order to be filled\n')
            price = self.price(symbol)
            if price > self.info['entry'] or price < self.info['entry']:
                self._log('\nRecalculating params\n')
                tp = self._profit_percent(tp_percent, side, price)
                sl = self._loss_percent(sl_percent, side, price)
                self._log(
                    f'\nParams Recalculated\n-------\nTP: {tp}\nSL: {sl}\nPrice: {price}\n')
                self._reopen(side, symbol, type, amount, price, sl, tp)
                self.info['entry'] = price
            sleep(20)

        while self.in_position(symbol):
            self._log('\nIn position\n')
            self._log_trade_info()
            sleep(20)

        self._log('\nClosing position\n')
        self._close_position()

    def _info_collect(self, strategy):
        """Sets info data from strategy

        strategy (Class Object) - Separate module created by client (see docs)
        """
        self.info.update(strategy.props)
        self.info.update(strategy.params)
        # Retrieve balance before trade
        self.info['balance'] = self.balance('USD', strategy.props['code'])
        self._log(f'Info retrieved: {self.info}')

    def _entry_engine(self, strategy):
        """Finds an entry

        strategy (Class Object) - Separate module created by client (see docs)
        """
        while not strategy.entry():
            self._log('\nLooking for entry...\n')
            self._log_stats()
            sleep(20)

        self._log('\nEntry found\n')

    def _log(self, message):
        """Logs message to output"""
        if not self.silent:
            print(message)

# ------------------------------ Helper Methods ------------------------------ #

    def in_position(self, symbol):
        """Returns True if in position for symbol, false otherwise

        symbol (String) - Symbol to check if in position for (ex. BTC/USD:USD)
        """
        return self._client.in_position(symbol)

# ----------------------------- Indicator Methods ---------------------------- #

    def macd(self, symbol, tf, params=None):
        """Returns the Moving Average Convergence Divergence indicator values

        symbol (String) - Trading pair
        tf (String) - Timeframe for macd values
        params (Dictionary) - Optional params able to change
                            - {"fastperiod": 9, "slowperiod": 12, "signalperiod": 3}
        """
        _, _, _, _, close, _ = self._indicator_client.ohlcv(
            self.exchange, symbol, tf)

        if not params:
            return self._indicator_client.macd(close)
        else:
            return self._indicator_client.macd(close, **params)

    def ema(self, symbol, tf, params=None):
        """Returns the Moving Average Convergence Divergence indicator values

        symbol (String) - Trading pair
        tf (String) - Timeframe for macd values
        params (Dictionary) - Optional params able to change
                            - {"timeperiod": 20}
        """
        _, _, _, _, close, _ = self._indicator_client.ohlcv(
            self.exchange, symbol, tf)

        if not params:
            return self._indicator_client.ema(close)
        else:
            return self._indicator_client.ema(close, **params)

# ------------------------------ Client Methods ------------------------------ #

    def _spot_engine(self):
        """Initiates trades within the spot market"""
        pass

    def engine(self, Strategy, limit=100):
        """Runs the strategy

        Strategy (Class) - Separate module created by client (see docs)
        limit (Int) - How many times the engine should run strategy (defaults at 100)
        """
        strategy = Strategy()
        # Initiate engine
        while self.stats['trades'] <= limit:
            # Wait for new minute
            self._log('\nSyncing\n')
            self._wait_to_start()
            # Find entry
            self._entry_engine(strategy)
            # Entry found
            self._info_collect(strategy)
            # Run market engine
            code = self.info['code']
            if code == 'future':
                self._future_engine()
            # Next trade
            self.stats['trades'] += 1
