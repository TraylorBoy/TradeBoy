"""Automated Crypto Trader for future market"""

from phemexboy.proxy import Proxy
from tradeboy.helpers.utility import sync
from tradeboy.helpers.calc import take_profit, stop_loss
from tradeboy.helpers.exceptions import InvalidParamError
from time import sleep

# TODO: Add cleanup method (make sure no position/orders open)
# TODO: Exit strategy
# TODO: Keep running after timeout error?
# TODO: Send logs to discord
# TODO: trailing stop loss
# TODO: Tools error handling and tests
# TODO: Refactor

class FutureEngine:
  def __init__(self, Strategy: object, rate: int = 20, verbose: bool = False):
    usd_balance = 0
    try:
      self._strategy = Strategy()
      self._proxy = Proxy(verbose=verbose)
      usd_balance = self._proxy.balance(currency='USD', code='future')
    except Exception as e:
      print(f'Failed to initialize engine: \n{e}')
    finally:
      self._rate = rate # Request rate
      self._verbose = verbose
      self._trade_stats = {
        "trade": 1,
        "wins": 0,
        "losses": 0
      }
      self._position_stats = {
        "entry": 0,
        "tp": 0,
        "sl": 0
      }
      self._wallet = {
        "balance": usd_balance,
        "pnl": 0,
      }
      self._log('Engine initialized...')

# ------------------------------- Class Methods ------------------------------ #

  def _log(self, msg: str, end: str = None):
    """Print message to output if not silent

    Args:
        msg (str): Message to print to output
        end (str): String appended after the last value. Default a newline.
    """
    if self._verbose:
        print(msg, end=end)

  def _find_entry(self):
    """Waits for strategy entry

    Raises:
      Exception: Failed to find entry
    """
    try:
      # Wait until strategy finds entry signal
      while not self._strategy.entry():
        sleep(self._rate)
    except Exception as e:
      print('Failed to find entry...')
      raise

  def _open_position(self):
    """Open a position

    Raises:
      Exception: Failed to place market order
      Exception: Failed to place limit order
      InvalidParamError: type can only be limit or market

    Returns
      OrderClient: Order object
    """
    type_of_trade = self._strategy.params['type']

    # Place either market or limit order
    if type_of_trade == 'market':
      try:
        self._log('Placing a market order...')
        return self._open_market_trade()
      except Exception as e:
        print('Failed to place market order')
        raise
    elif type_of_trade == 'limit':
      try:
        self._log('Placing a limit order...')
        return self._open_limit_trade()
      except Exception as e:
        print('Failed to place limit order')
        raise
    else:
      raise InvalidParamError('type can only be limit or market')

  def _open_market_trade(self):
    """Places a market order

    Raises:
      Exception: Failed to calculate tp/sl
      Exception: Failed to place long order
      Exception: Failed to place short order

    Returns
      OrderClient: Order object
    """
    type_of_trade = self._strategy.params['type']
    side = self._strategy.params['side']
    amount = self._strategy.params['amount']
    tp_percent = self._strategy.params['tp_percent']
    sl_percent = self._strategy.params['sl_percent']
    symbol = self._strategy.params['symbol']

    try:
      # Calculate tp and sl
      self._log('Calculating take profit and stop loss prices...')
      price = self._proxy.price(symbol)
      tp = take_profit(side, price, tp_percent)
      sl = stop_loss(side, price, sl_percent)
      self._log(f'\nTake Profit: {tp}\nStop Loss: {sl}\n')
    except Exception as e:
      print('Failed to calculate tp/sl')
      raise
    finally:
      self._position_stats['entry'] = price
      self._position_stats['tp'] = tp
      self._position_stats['sl'] = sl

    # Place order
    if side == 'long':
      try:
        self._log('Opening a long position...')
        return self._proxy.long(symbol, type_of_trade, amount, sl=sl, tp=tp)
      except Exception as e:
        print('Failed to place long order')
        raise
    elif side == 'short':
      try:
        self._log('Opening a short position...')
        return self._proxy.short(symbol, type_of_trade, amount, sl=sl, tp=tp)
      except Exception as e:
        print('Failed to place short order')
        raise
    else:
      raise InvalidParamError('side can only be long or short')

  def _open_limit_trade(self):
    """Places a limit order

    Raises:
      Exception: Failed to calculate tp/sl
      Exception: Failed to place long order
      Exception: Failed to place short order

    Returns
      OrderClient: Order object
    """
    type_of_trade = self._strategy.params['type']
    side = self._strategy.params['side']
    amount = self._strategy.params['amount']
    tp_percent = self._strategy.params['tp_percent']
    sl_percent = self._strategy.params['sl_percent']
    symbol = self._strategy.params['symbol']
    price = self._proxy.price(symbol)

    try:
      # Calculate tp and sl
      self._log('Calculating take profit and stop loss prices...')
      tp = take_profit(side, price, tp_percent)
      sl = stop_loss(side, price, sl_percent)
      self._log(f'\nTake Profit: {tp}\nStop Loss: {sl}\n')
    except Exception as e:
      print('Failed to calculate tp/sl')
      raise
    finally:
      self._position_stats['entry'] = price
      self._position_stats['tp'] = tp
      self._position_stats['sl'] = sl

    # Place order
    if side == 'long':
      try:
        self._log('Opening a long position...')
        return self._proxy.long(symbol, type_of_trade, amount, price=price, sl=sl, tp=tp)
      except Exception as e:
        print('Failed to place long order')
        raise
    elif side == 'short':
      try:
        self._log('Opening a short position...')
        return self._proxy.short(symbol, type_of_trade, amount, price=price, sl=sl, tp=tp)
      except Exception as e:
        print('Failed to place short order')
        raise
    else:
      raise InvalidParamError('side can only be long or short')

  def _manage_position(self):
    """Manage open position

    Raises
      Exception: Failed to close position
      Exception: Failed to find exit strategy
      InvalidParamError: exit must be either True or False
    """
    exit_strategy = self._strategy.params['exit']
    # Check if there is an exit strategy already in place
    # If not then waits for tp/sl to get hit
    if not exit_strategy:
      try:
        self._close_position()
      except Exception as e:
        print('Failed to close position')
        raise
    elif exit_strategy:
      try:
        self._find_exit()
      except Exception as e:
        print('Failed to find exit strategy')
        raise
    else:
      raise InvalidParamError('exit must be either True or False')

  def _close_position(self):
    """Waits for position to be closed

    Raises:
      Exception: Failed to retrieve position
      Exception: Failed to close position
    """
    symbol = self._strategy.params['symbol']

    try:
      # Get open position
      self._log('Retrieving position...')
      position = self._proxy.position(symbol)
      self._log(f'Position found: \n{position}')
    except Exception as e:
      print('Failed to retrieve position')
      raise

    try:
      # Wait for position to be closed
      self._log('Waiting for position to be closed...')
      while not position._check_closed():
        self.view_position_stats()
        sleep(self._rate)
    except Exception as e:
      print('Failed to check if position was closed')
      raise

  # TODO
  def _find_exit(self):
    pass

  def _update_data(self):
    """Update trade stats and wallet

    Raises:
      Exception - Failed to update wallet
    """
    self._trade_stats['trade'] += 1
    prev_balance = self._wallet['balance']

    try:
      self._wallet['balance'] = self._proxy.balance(currency='USD', code='future')
    except Exception as e:
      print('Failed to update wallet')
      raise
    finally:
      # Update profit and loss
      self._wallet['pnl'] += self._wallet['balance'] - prev_balance
      # Win
      if prev_balance < self._wallet['balance']:
        self._trade_stats['wins'] += 1
      # Loss
      if prev_balance > self._wallet['balance']:
        self._trade_stats['losses'] += 1

# ------------------------------ Client Methods ------------------------------ #

  def verbose(self):
      """Turn on logging"""
      self._verbose = True

  def silent(self):
      """Turn off logging"""
      self._verbose = False

  def view_trade_stats(self):
    """Output stats"""
    print(f'\nTrade: {self._trade_stats["trade"]}\nWins: {self._trade_stats["wins"]}\nLosses: {self._trade_stats["losses"]}\n')

  def view_position_stats(self):
    """Output position stats

    Raises:
      Exception - Failed to retrieve price and view position stats
    """
    try:
      print(f'\nPrice: {self._proxy.price(self._strategy.params["symbol"])}\nEntry: ${self._position_stats["entry"]}\nTake Profit: ${self._position_stats["tp"]}\nStop Loss: ${self._position_stats["sl"]}\n')
    except Exception as e:
      print('Failed to retrieve price and view position stats')
      raise

  def view_wallet(self):
    """Output wallet information"""
    print(f'\nBalance: ${self._wallet["balance"]}\nProfit/Loss: {self._wallet["pnl"]} (USD)\n')

  def run(self, trades: int = 1):
    """Run the strategy

    Args:
        trades (int, optional): Total number of trades to run. Defaults to 1.
    """

    while self._trade_stats['trade'] <= trades:
      try:
        # Wait until next minute
        self._log('Syncing...')
        sync()
        # Find entry
        self.view_trade_stats()
        self.view_wallet()
        self._log('Finding entry...')
        self._find_entry()
        # Open position
        self._log('Opening a position...')
        order = self._open_position()
        self._log(f'Order found: \{order}')
        # Check if order was closed
        self._log('Checking if order was closed...')
        # TODO: Refactor
        if order.closed():
          self._log(f'Order closed, position opened...')
          # Mange open position
          self._manage_position()
          # Trade finished
          # Update trade data
          self._log('Trade complete, updating trade data...')
          self._update_data()
        else:
          tp_percent = self._strategy.params['tp_percent']
          sl_percent = self._strategy.params['sl_percent']
          # Limit order
          # Will try to close order for 1 minute
          if order.close(True, tries=60, sl_percent=sl_percent, tp_percent=tp_percent):
            self._log(f'Order closed, position opened...')
            # Mange open position
            self._manage_position()
            # Trade finished
            # Update trade data
            self._log('Trade complete, updating trade data...')
            self._update_data()
          else:
            # Order failed to close
            self._log('Order failed to close, cancelling...')
            if order.pending(): order.cancel()
      except InvalidParamError as e:
        print(f'Strategy contains invalid params: \n{e}')
      except Exception as e:
        print(f'Error while running strategy: \n{e}')
        break
        # TODO: Cleanup method
