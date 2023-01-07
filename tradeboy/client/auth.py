"""Authentication Client"""

import os

from phemexboy import PhemexBoy


class AuthClient:
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
        self._log('Connecting to Phemex Authentication Endpoint')
        try:
            self._client = PhemexBoy(
                os.getenv('PHEMEX_KEY'), os.getenv('PHEMEX_SECRET'))
        except Exception as e:
            self._log(e)
            raise Exception(
                f'Failed to connect to Phemex Authentication Endpoint')

# ------------------------------ Client Methods ------------------------------ #

    def balance(self, of, code='spot'):
        """Retrieve balance from specific account

        of (String) - Asset to retrieve balance for
        code (String) - Values should be either spot or future to indicate which
        account to retrieve balance for (default is swap due to not every
        exchange having a future option)
        """
        bal = None

        self._log(
            f'Retrieving balance from {self._exchange} for {of} on {code} market')
        try:
            if code == 'spot':
                bal = self._client.balance(of)
            elif code == 'future':
                bal = self._client.future_balance(of)
            else:
                raise Exception('Invalid code')
        except Exception as e:
            self._log(e)
            raise Exception(f'Failed retrieving balance')

        self._log(f'Retrieved balance: {round(bal, 2)}')
        return bal

    def open_position(self, side, symbol, type, amount, price, sl, tp):
        """Opens a position within the future market"""
        self._log(f'Opening a position on {self._exchange}')
        self._log(
            f'Params:\nSide: {side}\nSymbol: {symbol}\nType: {type}\nAmount: {amount}\nPrice: {price}\nSL: {sl}\nTP: {tp}')
        try:
            if side == 'long':
                # Open long position
                self._client.long(symbol, type, amount, price, sl, tp)

            elif side == 'short':
                # Open short position
                self._client.short(symbol, type, amount, price, sl, tp)
        except Exception as e:
            self._log(e)
            raise Exception(f'Failed to open a position')

    def reopen_position(self, side, symbol, type, amount, price, sl, tp):
        """Cancel pending order and reopen position"""
        self._log(f'Reopening position on {self._exchange}')
        try:
            # Cancel order
            self._client.cancel_all(symbol)
            # Reopen position
            self.open_position(side, symbol, type, amount, price, sl, tp)
        except Exception as e:
            self._log(e)
            raise Exception(f'Failed to reopen position')

    def in_position(self, symbol):
        """Returns True if in position for symbol, false otherwise

        symbol (String) - Symbol to check if in position for (ex. BTC/USD:USD)
        """
        self._log(f'Checking if in position for {symbol} on {self._exchange}')
        try:
            return self._client.in_position(symbol)
        except Exception as e:
            self._log(e)
            raise Exception(f'Failed to check position status')
