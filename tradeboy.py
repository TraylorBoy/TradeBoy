"""Automated Crypto Trader"""

import os

from candleboy import CandleBoy
from phemexboy import PhemexBoy
from dotenv import load_dotenv
load_dotenv()


class TradeBoy:
    def __init__(self, exchange):
        self.candleboy = CandleBoy()

        if exchange == 'phemex':
            self.exchange = exchange
            self.client = PhemexBoy(
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
            bal = self.client.balance(of)
        elif code == 'future':
            bal = self.client.future_balance(of)
        else:
            raise Exception('Invalid code')

        return bal

    def price(self, symbol):
        """Returns the last price of symbol

        symbol (String) - Trading pair
        """
        return self.client.price(symbol)

    def macd(self, symbol, tf, params=None):
        """Returns the Moving Average Convergence Divergence indicator values

        symbol (String) - Trading pair
        tf (String) - Timeframe for macd values
        params (Dictionary) - Optional params able to change
                            - {"fastperiod": 9, "slowperiod": 12, "signalperiod": 3}
        """
        if self.exchange == 'phemex':
            _, _, _, _, close, _ = self.candleboy.ohlcv(
                self.exchange, symbol, tf)
            if not params:
                return self.candleboy.macd(close)
            else:
                return self.candleboy.macd(close, params)

# ------------------------------ Client Methods ------------------------------ #

    def engine(self, Strategy):
        """Runs the strategy

        Strategy (Class) - Separate module created by client (see docs)
        """
        strategy = Strategy()
        strategy.entry()
