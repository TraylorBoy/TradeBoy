"""Calculations helper"""

def take_profit(side: str, price: float, percent: float):
  """Calculate take profit price

  Args:
      side (str): Trade side (ex. 'long' or 'short')
      price (float): Price to calculate take profit for
      percent (float): Take profit percent

  Returns:
      Float: Take profit price
  """
  if side == 'long': return price + (price * (percent / 100))
  if side == 'short': return price - (price * (percent / 100))

def stop_loss(side: str, price: float, percent: float):
  """Calculate stop loss price

  Args:
      side (str): Trade side (ex. 'long' or 'short')
      price (float): Price to calculate stop loss for
      percent (float): Stop loss percent

  Returns:
      Float: Stop loss price
  """
  if side == 'long': return price - (price * (percent / 100))
  if side == 'short': return price + (price * (percent / 100))
