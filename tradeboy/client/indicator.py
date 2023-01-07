"""Indicator Client"""

from candleboy import CandleBoy


class IndicatorClient:
    def __init__(self, exchange, silent=True):
        self._silent = silent
        self._exchange = exchange
        # Connect to endpoint
        self._log('Connecting to Indicator Endpoint')
        try:
            self._client = CandleBoy()
        except Exception as e:
            self._log(e)
            raise Exception(f'Failed connecting to Indicator Endpoint')

# ------------------------------- Class Methods ------------------------------ #

    def _log(self, message):
        """Outputs message if not silent

        message (String) - Message to output
        """
        if not self._silent:
            print(f'\n{message}\n')

# ------------------------------ Client Methods ------------------------------ #

    def macd(self, symbol, tf, params=None):
        """Returns the Moving Average Convergence Divergence indicator values

        symbol (String) - Trading pair
        tf (String) - Timeframe for macd values
        params (Dictionary) - Optional params able to change
                            - {"fastperiod": 9, "slowperiod": 12, "signalperiod": 3}
        """
        self._log(
            f'Retrieving MACD values from {self._exchange} for {symbol}, {tf}')
        try:
            _, _, _, _, close, _ = self._client.ohlcv(
                self._exchange, symbol, tf)

            macd = None
            if not params:
                macd = self._client.macd(close)
            else:
                macd = self._client.macd(close, **params)

            self._log(f'Retrieved MACD: {macd}')
            return macd
        except Exception as e:
            self._log(e)
            raise Exception('Failed to retrieve MACD indicator values')

    def ema(self, symbol, tf, params=None):
        """Returns the Moving Average Convergence Divergence indicator values

        symbol (String) - Trading pair
        tf (String) - Timeframe for macd values
        params (Dictionary) - Optional params able to change
                            - {"timeperiod": 20}
        """
        self._log(
            f'Retrieving EMA values from {self._exchange} for {symbol}, {tf}')
        try:
            _, _, _, _, close, _ = self._client.ohlcv(
                self._exchange, symbol, tf)

            ema = None
            if not params:
                ema = self._client.ema(close)
            else:
                ema = self._client.ema(close, **params)

            self._log(f'Retrieved EMA: {ema}')
            return ema
        except Exception as e:
            self._log(e)
            raise Exception('Failed to retrieve EMA indicator values')
