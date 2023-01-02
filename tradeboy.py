"""Automated Crypto Trader"""

import os

from time import sleep
from candleboy import CandleBoy
from phemexboy import PhemexBoy
from dotenv import load_dotenv
load_dotenv()

# TODO: Error handling
# TODO: Future engine
# TODO: Spot engine
# TODO: Create unified symbol for both spot and future
# TODO: Fix docstrings


class TradeBoy:
    EXCHANGES = ['phemex']
    CODES = ['spot', 'future', 'buy', 'sell', 'long', 'short']

    def __init__(self, exchange):
        if exchange not in self.EXCHANGES:
            raise Exception(f'{exchange} is not supported')

        # Setup class properties
        self._candleboy = CandleBoy()
        self._exchange = exchange
        self._in_trade = False
        self._load()

# ------------------------------- Class Methods ------------------------------ #

    def _load(self):
        """Connects to exchange client endpoint"""
        if self._exchange == 'phemex':
            self._client = PhemexBoy(
                os.getenv('PHEMEX_KEY'), os.getenv('PHEMEX_SECRET'))

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
        _, _, _, _, close, _ = self._candleboy.ohlcv(
            self._exchange, symbol, tf)

        if not params:
            return self._candleboy.macd(close)
        else:
            return self._candleboy.macd(close, **params)

    def ema(self, symbol, tf, params=None):
        """Returns the Moving Average Convergence Divergence indicator values

        symbol (String) - Trading pair
        tf (String) - Timeframe for macd values
        params (Dictionary) - Optional params able to change
                            - {"timeperiod": 20}
        """
        _, _, _, _, close, _ = self._candleboy.ohlcv(
            self._exchange, symbol, tf)

        if not params:
            return self._candleboy.ema(close)
        else:
            return self._candleboy.ema(close, **params)

# ------------------------------ Client Methods ------------------------------ #

    def engine(self, Strategy, limit=100):
        """Runs the strategy

        Strategy (Class) - Separate module created by client (see docs)
        limit (Int) - How many times the engine should run strategy
        """
        strategy = Strategy()
        props = strategy.props
        stats = {"wins": 0, "losses": 0, "profit": 0}
        starting_balance = self.balance('USD', strategy.props['code'])
        entry = None
        params = None
        i = 0

        while i <= limit:

            while not strategy.entry():
                print('\nLooking for entry...\n')
                print(
                    f'Stats\n-------\nWins: {stats["wins"]}\nLosses: {stats["losses"]}\nProfit: {stats["profit"]}%\nTrades: {i}')
                sleep(20)

            # Entry found
            params = strategy.params

            while not self._in_trade:
                if strategy.code == 'future':
                    if params['side'] == 'long':
                        # Open long position
                        self._client.long(
                            symbol=props['symbol'], type=params['type'], amount=params['amount'], price=params['price'], sl=params['sl'], tp=params['tp'])
                        self._in_trade = True
                        entry = self.price(props['symbol'])

                    elif params['side'] == 'short':
                        # Open short position
                        self._client.short(
                            symbol=props['symbol'], type=params['type'], amount=params['amount'], price=params['price'], sl=params['sl'], tp=params['tp'])
                        self._in_trade = True
                        entry = self.price(props['symbol'])

            while self._in_trade:
                price = self.price(props['symbol'])
                tp = params['tp']
                sl = params['sl']
                side = params['side']
                balance = round(self.balance('USD', code='future'), 2)

                print(
                    f'\nIn Trade\n-------\nside: {side}\nBalance: ${balance}\nPrice: ${price}\nEntry: ${entry}\nTP: ${tp}\nSL: ${sl}\n')
                print(
                    f'Stats\n-------\nWins: {stats["wins"]}\nLosses: {stats["losses"]}\nProfit: {stats["profit"]}%\nTrades: {i}')

                if side == 'long':
                    if price >= tp and not self.in_position(symbol=props['symbol']):
                        self._in_trade = False
                        stats["wins"] += 1
                        stats["profit"] += 0.20

                    if price <= sl and not self.in_position(symbol=props['symbol']):
                        self._in_trade = False
                        stats["losses"] += 1
                        stats["profit"] -= 0.10

                if side == 'short':
                    if price <= tp and not self.in_position(symbol=props['symbol']):
                        self._in_trade = False
                        stats["wins"] += 1
                        stats["profit"] += 0.20
                    if price >= sl and not self.in_position(symbol=props['symbol']):
                        self._in_trade = False
                        stats["losses"] += 1
                        stats["profit"] -= 0.10

                sleep(20)
            i += 1
            print(
                f'\nStats\n-------\nWins: {stats["wins"]}\nLosses: {stats["losses"]}\nProfit: {stats["profit"]}%\nTrades: {i}\n')
            sleep(10)
