"""Public Client"""

from phemexboy import PhemexBoy


class PublicClient:
    def __init__(self, exchange, silent=True):
        self._silent = silent
        self._exchange = exchange
        # Connect to endpoint
        setup = {
            "phemex": self._setup_phemex
        }
        setup[exchange]()

# ------------------------------- Class Methods ------------------------------ #

    def _log(self, message):
        """Outputs message if not silent"""
        if not self._silent:
            print(f'\n{message}\n')

    def _setup_phemex(self):
        """Connect to Phemex exchange"""
        self._log('Connecting to Phemex Public Endpoint')
        try:
            self._client = PhemexBoy()
        except Exception as e:
            self._log(e)
            raise Exception(
                f'Failed to connect to Phemex Public Endpoint')

# ------------------------------ Client Methods ------------------------------ #

    def price(self, symbol):
        """Returns the last price of symbol

        symbol (String) - Trading pair
        """
        self._log(f'Retrieving price from {self._exchange} for {symbol}')
        try:
            price = self._client.price(symbol)
            self._log(f'Retrieved price: {round(price, 2)}')
            return price
        except Exception as e:
            self._log(e)
            raise Exception(f'Failed retrieving price')
