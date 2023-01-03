"""Automated Crypto Trader"""

import os

from time import sleep
from candleboy import CandleBoy
from phemexboy import PhemexBoy
from dotenv import load_dotenv
load_dotenv()

# TODO: Error handling (CODES?)
# TODO: Spot engine
# TODO: Create unified symbol for both spot and future
# TODO: Fix docstrings
# TODO: Add logger
# TODO: GUI
# TODO: Figure out how to not double init (in strategy and to use engine) - Class methods?
# TODO: Add CoinbaseBoy
# TODO: Add more indicators - Test more strategies (will have to work on CandleBoy as well)


class TradeBoy:
    EXCHANGES = ['phemex']
    CODES = ['spot', 'future', 'buy', 'sell', 'long', 'short']

    def __init__(self, exchange):
        if exchange not in self.EXCHANGES:
            raise Exception(f'{exchange} is not supported')

        # Setup class properties
        self.exchange = exchange
        self.stats = {'wins': 0, 'losses': 0, 'profit': 0, 'trades': 0}
        self.info = {}
        # Connect to necessary clients
        self._connect()

# ------------------------------- Class Methods ------------------------------ #

    def _connect(self):
        """Connects to exchange client endpoint"""
        # Connect to indicator client
        self._indicator_client = CandleBoy()
        # Connect to exchange client
        if self.exchange == 'phemex':
            self._client = PhemexBoy(
                os.getenv('PHEMEX_KEY'), os.getenv('PHEMEX_SECRET'))

    def _log_trade_info(self):
        """Outputs trade information"""
        side = self.info['side']
        symbol = self.info['symbol']
        amount = self.info['amount']
        sl = self.info['sl']
        tp = self.info['tp']
        code = self.info['code']
        entry = self.stats['entry']

        price = self.price(symbol)
        balance = round(self.balance('USD', code), 2)

        print(
            f'\nTrade Information\n----------\nSide: {side}\nBalance: ${balance}\nPrice: ${price}\nEntry: ${entry}\nTP: ${tp}\nSL: ${sl}\nAmount: {amount}')
        self._log_stats()

    def _log_stats(self):
        """Displays stats to output"""
        wins = self.stats['wins']
        losses = self.stats['losses']
        profit = round(self.stats['profit'], 2)
        trades = self.stats['trades']

        print(
            f'\nStats\n-------\nWins: {wins}\nLosses: {losses}\nProfit: {profit} (USD)\nTrades: {trades}\n')

    def _open_position(self, side, symbol, type, amount, price, sl, tp):
        """Opens a position within the future market"""
        if side == 'long':
            # Open long position
            self._client.long(symbol, type, amount, price, sl, tp)
            self.intro['entry'] = self.price(symbol)

        elif side == 'short':
            # Open short position
            self._client.short(symbol, type, amount, price, sl, tp)
            self.info['entry'] = self.price(symbol)

    def _calculate_profit(self):
        """Returns current profit or loss"""
        code = self.info['code']
        starting_bal = self.info['balance']
        bal = self.balance('USD', code)

        if starting_bal > bal:
            return round(starting_bal - bal, 2)
        if starting_bal < bal:
            return round(bal - starting_bal, 2)

    def _win(self):
        """Updates win stats"""
        self.stats['wins'] += 1
        self.stats['profit'] += self._calculate_profit()

    def _loss(self):
        """Updates win stats"""
        self.stats['losses'] += 1
        self.stats['profit'] -= self._calculate_profit()

    def _close_position(self, symbol, side, tp, sl):
        """Checks if tp or sl has triggered and updates stats"""
        if side == 'long':
            if self.price(symbol) >= tp:
                self._win()

            if self.price(symbol) <= sl:
                self._loss()

        if side == 'short':
            if self.price(symbol) <= tp:
                self._win()
            if self.price(symbol) >= sl:
                self._loss()

    def _future_engine(self):
        """Initiates trades within the future market"""
        side = self.info['side']
        symbol = self.info['symbol']
        amount = self.info['amount']
        price = self.info['price']
        sl = self.info['sl']
        tp = self.info['tp']
        type = self.info['type']

        while not self.in_position(symbol):
            self._open_position(side, symbol, type, amount, price, sl, tp)

        while self.in_position(symbol):
            self._log_trade_info()
            self._close_position(symbol, side, tp, sl)
            sleep(20)

    def _info_collect(self, strategy):
        """Sets info data from strategy

        strategy (Class Object) - Separate module created by client (see docs)
        """
        self.info.update(strategy.props)
        self.info.update(strategy.params)
        self.info['balance'] = self.balance('USD', strategy.props['code'])

    def _entry_engine(self, strategy):
        """Finds an entry

        strategy (Class Object) - Separate module created by client (see docs)
        """
        while not strategy.entry():
            # TODO: Move to logger
            print('\nLooking for entry...\n')
            self._log_stats()
            sleep(20)


# ------------------------------ Helper Methods ------------------------------ #

    def balance(self, of, code='spot'):
        """Retrieve balance from specific account

        of (String) - Asset to retrieve balance for
        code (String) - Values should be either spot or future to indicate which
        account to retrieve balance for (default is swap due to not every
        exchange having a future option)
        """
        bal = None

        if code == 'spot':
            bal = self._client.balance(of)
        elif code == 'future':
            bal = self._client.future_balance(of)
        else:
            raise Exception('Invalid code')

        return bal

    def price(self, symbol):
        """Returns the last price of symbol

        symbol (String) - Trading pair
        """
        return self._client.price(symbol)

    def in_position(self, symbol):
        """Returns True if in position for symbol, false otherwise

        symbol (String) - Symbol to check if in position for (ex. BTC/USD:USD)
        """
        return self._client.in_position(symbol)

    def profit_percent(self, symbol, percent, side):
        """Calculates take profit price based off of percentage from current price

        symbol (String) - Symbol to calculate profit price for (ex. BTC/USD:USD)
        percent (Integer) - Percent to calculate profit price
        side (String) - What side of the trade you are on (ex. long, short, buy, sell)
        """
        price = self.price(symbol)
        if side == 'long':
            return round(price + (price * (percent / 100)), 2)
        if side == 'short':
            return round(price - (price * (percent / 100)), 2)

    def loss_percent(self, symbol, percent, side):
        """Calculates stop loss price based off of percentage from current price

        symbol (String) - Symbol to calculate stop loss price for (ex. BTC/USD:USD)
        percent (Integer) - Percent to calculate stop loss price
        side (String) - What side of the trade you are on (ex. long, short, buy, sell)
        """
        price = self.price(symbol)
        if side == 'long':
            return round(price - (price * (percent / 100)), 2)
        if side == 'short':
            return round(price + (price * (percent / 100)), 2)

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

        while self.stats['trades'] <= limit:
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
