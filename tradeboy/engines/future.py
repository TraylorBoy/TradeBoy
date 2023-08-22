"""Automated Crypto Trader for future market"""

from phemexboy.proxy import Proxy
from tradeboy.helpers.utility import sync
from time import sleep

# TODO: Add error handling
# TODO: Exit strategy, limit
# TODO: Refactor
# TODO: Better logging

class FutureEngine:
  def __init__(self, Strategy: object, rate: int = 20, verbose: bool = False):
    self._strategy = Strategy()
    self._rate = rate # Request rate
    self._verbose = verbose
    self._proxy = Proxy(verbose)

# ------------------------------- Class Methods ------------------------------ #

  def _log(self, msg: str, end: str = None):
    """Print message to output if not silent

    Args:
        msg (str): Message to print to output
        end (str): String appended after the last value. Default a newline.
    """
    if self._verbose:
        print(msg, end=end)

# ------------------------------ Client Methods ------------------------------ #

  def run(self, trades: int = 1):
    """Run the strategy

    Args:
        trades (int, optional): Total number of trades to run. Defaults to 1.
    """
    # Wait until next minute
    self._log('Syncing...', ',')
    sync()
    self._log('done.')

    trade = 1
    while trade <= trades:
      self._log(f'Current trade: {trade}')

      # Find entry
      while not self._strategy.entry():
        self._log('Finding entry...')
        sleep(self._rate)

      # Entry found
      type_of_trade = self._strategy.params['type']
      side = self._strategy.params['side']
      amount = self._strategy.params['amount']
      tp = self._strategy.params['tp']
      sl = self._strategy.params['sl']
      symbol = self._strategy.params['symbol']
      exit_strategy = self._strategy.params['exit']

      # Open position
      order = None
      position = None

      self._log('Opening position...')
      if type_of_trade == 'market':
        if side == 'long':
          # Calculate tp and sl
          price = self._proxy.price(symbol)
          sl = price - (price * sl)
          tp = price + (price * tp)

          order = self._proxy.long(symbol, type_of_trade, amount, sl, tp)
        elif side == 'short':
          # Calculate tp and sl
          price = self._proxy.price(symbol)
          sl = price + (price * sl)
          tp = price - (price * tp)

          order = self._proxy.short(symbol, type_of_trade, amount, sl, tp)
        else:
          # TODO: Error handling
          pass

        # Get position data
        self._log(f'Retrieved order {order}')
        if order.closed():
          position = self._proxy.position(symbol)
          self._log(f'Retrieved position {position}')
      elif type_of_trade == 'limit':
        pass
      else:
        # TODO: Error handling
        pass

      # Manage open position
      if not exit_strategy:
        # Wait for position to be closed
        while not position._check_closed():
          self._log('Waiting for position to be closed...')
          sleep(self._rate)
      else:
        # TODO: Exit strategy
        pass

      # Update trade data
      trades += 1

      def verbose(self):
          """Turn on logging"""
          self._verbose = True

      def silent(self):
          """Turn off logging"""
          self._verbose = False
