"""Client Proxy"""


from .indicator import IndicatorClient
from .public import PublicClient
from .auth import AuthClient
from dotenv import load_dotenv
load_dotenv()


class Proxy:
    EXCHANGES = ['phemex']

    def __init__(self, exchange, silent=True):
        if exchange not in self.EXCHANGES:
            raise Exception(f'{exchange} is not supported')

        self._indicator_endpoint = IndicatorClient(exchange, silent)
        self._pub_endpoint = PublicClient(exchange, silent)
        self._auth_endpoint = AuthClient(exchange, silent)

# ------------------------------ Public Methods ------------------------------ #

    def price(self, symbol):
        """Returns the last price of symbol

        symbol (String) - Trading pair
        """
        return self._pub_endpoint.price(symbol)

# ------------------------------- Auth Methods ------------------------------- #

    def balance(self, of, code='spot'):
        """Retrieve balance from specific account

        of (String) - Asset to retrieve balance for
        code (String) - Values should be either spot or future to indicate which
        account to retrieve balance for (default is swap due to not every
        exchange having a future option)
        """
        return self._auth_endpoint.balance(of, code)

    def open_position(self, side, symbol, type, amount, price, sl, tp):
        """Opens a position within the future market"""
        self._auth_endpoint.open_position(
            side, symbol, type, amount, price, sl, tp)

    def reopen_position(self, side, symbol, type, amount, price, sl, tp):
        """Cancel pending order and reopen position"""
        self._auth_endpoint.reopen_position(
            side, symbol, type, amount, price, sl, tp)

    def in_position(self, symbol):
        """Returns True if in position for symbol, false otherwise

        symbol (String) - Symbol to check if in position for (ex. BTC/USD:USD)
        """
        return self._auth_endpoint.in_position(symbol)

# ----------------------------- Indicator Methods ---------------------------- #

    def macd(self, symbol, tf, params=None):
        """Returns the Moving Average Convergence Divergence indicator values

        symbol (String) - Trading pair
        tf (String) - Timeframe for macd values
        params (Dictionary) - Optional params able to change
                            - {"fastperiod": 9, "slowperiod": 12, "signalperiod": 3}
        """
        return self._indicator_endpoint.macd(symbol, tf, params)

    def ema(self, symbol, tf, params=None):
        """Returns the Moving Average Convergence Divergence indicator values

        symbol (String) - Trading pair
        tf (String) - Timeframe for macd values
        params (Dictionary) - Optional params able to change
                            - {"timeperiod": 20}
        """
        return self._indicator_endpoint.ema(symbol, tf, params)
