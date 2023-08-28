"""Strategy helpers"""

from phemexboy.proxy import Proxy
from candleboy.core import CandleBoy

class Tools:
  def __init__(self, exchange: str, verbose: bool = False):
    try:
      self.proxy = Proxy(verbose)
      self.candle = CandleBoy(exchange, verbose)
    except Exception as e:
      print(f'Failed to initialize tools: \n{e}')

  def symbol(self, base: str, quote: str, code: str):
    """Creates a symbol representing the asset pairing

    Args:
        base (str): Currency you are buying (ex. 'btc')
        quote (str): Currency you are selling (ex. 'usd')
        code (str): Market code (ex. 'spot')

    Returns:
        String: Formatted base and quote currency symbol
    """
    return self.proxy.symbol(base, quote, code)

  def price(self, symbol: str):
    """Retrieve price of asset pair

    Args:
        symbol (str): Created symbol for base and quote currencies

    Raises:
        NetworkError: PublicClient failed to retrieve price for {symbol}
        ExchangeError: PublicClient failed to retrieve price for {symbol}
        Exception: PublicClient failed to retrieve price for {symbol}

    Returns:
        Float: Current ask price for base currency
    """
    try:
      return self.proxy.price(symbol)
    except Exception as e:
      print(f'Failed to retrieve price: \n{e}')

  def ohlcv(self, symbol: str, tf: str, since: str = None):
    """Retrieve the open - high - low - close - volume data from exchange

    Args:
        symbol (str): Pairing to retrieve OHLCV data for
        tf (str): Timeframe for OHLCV data
        since (str, optional): Optional start date for retrieving OHLCV data. Format as YEAR-MONTH-DAY (ex. 2018-12-01). Defaults to None.

    Returns:
        Tuple: open - high - low - close - volume data
    """
    try:
      return self.candle.ohlcv(symbol, tf, since)
    except Exception as e:
      print(f'Failed to retrieve OHLCV values: \n{e}')

  def macd(self, close: list, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9):
    """Returns the Moving Average Convergence/Divergence indicator values

    See TA-Lib docs for details on parameters.
    https://ta-lib.github.io/ta-lib-python/
    """
    return self.candle.macd(close, fastperiod, slowperiod, signalperiod)

  def ema(self, close: list, timeperiod: int = 200):
    """Returns the Exponential Moving Average indicator values

    See TA-Lib docs for details on parameters.
    https://ta-lib.github.io/ta-lib-python/
    """
    return self.candle.ema(close, timeperiod)

  def stoch(self, high: list, low: list, close: list, fastk_period: int = 5, slowk_period: int = 3, slowk_matype: int = 0, slowd_period: int = 3, slowd_matype: int = 0):
    """Returns the Stochastic indicator values

    See TA-Lib docs for details on parameters.
    https://ta-lib.github.io/ta-lib-python/
    """
    return self.candle.stoch(high, low, close, fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype)

  def adx(self, high: list, low: list, close: list, timeperiod: int = 14):
    """Returns the ADX indicator values

    See TA-Lib docs for details on parameters.
    https://ta-lib.github.io/ta-lib-python/
    """
    return self.candle.adx(high, low, close, timeperiod)

  def mesa(self, close: list, fastlimit: int = 0.5, slowlimit: int = 0.05):
    """Returns the MESA indicator values

    See TA-Lib docs for details on parameters.
    https://ta-lib.github.io/ta-lib-python/
    """
    return self.candle.mesa(close, fastlimit, slowlimit)
