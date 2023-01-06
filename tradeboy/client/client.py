"""Exchange Client"""

import os

from phemexboy import PhemexBoy
from candleboy import CandleBoy
from dotenv import load_dotenv
load_dotenv()


class IndicatorClient:
    def __init__(self, exchange, silent=True):
        self._silent = silent
        self._exchange = exchange
        # Connect to endpoint
        self._log('Connecting to Indicator Endpoint')
        try:
            self._client = CandleBoy()
        except Exception as e:
            raise Exception(f'Failed connecting to Indicator Endpoint:\n{e}')

# ------------------------------- Class Methods ------------------------------ #

    def _log(self, message):
        """Outputs message if not silent"""
        if not self._silent:
            print(f'\n{message}\n')


class AuthClient:
    def __init__(self, exchange, silent=True):
        self._silent = silent
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
        self._log('Connecting to Phemex Authentication Endpoint')
        try:
            self._client = PhemexBoy(
                os.getenv('PHEMEX_KEY'), os.getenv('PHEMEX_SECRET'))
        except Exception as e:
            raise Exception(
                f'Failed to connect to Phemex Authentication Endpoint:\n{e}')

# ------------------------------ Client Methods ------------------------------ #

    def balance(self, of, code='spot'):
        """Retrieve balance from specific account

        of (String) - Asset to retrieve balance for
        code (String) - Values should be either spot or future to indicate which
        account to retrieve balance for (default is swap due to not every
        exchange having a future option)
        """
        bal = None

        try:
            if code == 'spot':
                bal = self._client.balance(of)
            elif code == 'future':
                bal = self._client.future_balance(of)
            else:
                raise Exception('Invalid code')
        except Exception as e:
            raise (f'Failed retrieving balance:\n{e}')

        return bal


class PublicClient:
    def __init__(self, exchange, silent=True):
        self._silent = silent
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
            raise Exception(
                f'Failed to connect to Phemex Public Endpoint:\n{e}')

# ------------------------------ Client Methods ------------------------------ #

    def price(self, symbol):
        """Returns the last price of symbol

        symbol (String) - Trading pair
        """
        try:
            return self._client.price(symbol)
        except Exception as e:
            raise Exception(f'Failed retrieving price:\n{e}')


class Client:
    EXCHANGES = ['phemex']

    def __init__(self, exchange, silent=True):
        if exchange not in self.EXCHANGES:
            raise Exception(f'{exchange} is not supported')

        self._silent = silent

        try:
            self._indicator = IndicatorClient(exchange, silent)
            self._pub_endpoint = PublicClient(exchange, silent)
            self._auth_endpoint = AuthClient(exchange, silent)
        except Exception as e:
            raise (e)

# ------------------------------- Class Methods ------------------------------ #

    def _log(self, message):
        """Outputs message if not silent"""
        if not self._silent:
            print(f'\n{message}\n')

# ------------------------------ Public Methods ------------------------------ #

    def price(self, symbol):
        """Returns the last price of symbol

        symbol (String) - Trading pair
        """
        try:
            return self._pub_endpoint.price(symbol)
        except Exception as e:
            raise (e)

# ------------------------------- Auth Methods ------------------------------- #

    def balance(self, of, code='spot'):
        """Retrieve balance from specific account

        of (String) - Asset to retrieve balance for
        code (String) - Values should be either spot or future to indicate which
        account to retrieve balance for (default is swap due to not every
        exchange having a future option)
        """
        try:
            return self._auth_endpoint.balance(of, code)
        except Exception as e:
            raise (e)
