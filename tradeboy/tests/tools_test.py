"""Tests Tools"""

import unittest
from tradeboy.tools import Tools

class TestTools(unittest.TestCase):
  def test_init(self):
    tools = Tools(exchange='phemex', verbose=True)
    self.assertEqual(isinstance(tools, Tools), True)

  def test_methods(self):
    tools = Tools(exchange='phemex', verbose=True)

    symbol = tools.symbol(base='BTC', quote='USD', code='future')
    self.assertEqual(symbol, 'BTC/USD:USD')

    price = tools.price(symbol=symbol)
    self.assertGreater(price, 0)

    timestamps, o, h, l, c, v = tools.ohlcv(symbol=symbol, tf='4h', since=None)
    self.assertGreater(len(list(c)), 0)

    macd, _, _ = tools.macd(close=c)
    self.assertGreater(len(list(macd)), 0)

    ema = tools.ema(close=c)
    self.assertGreater(len(list(ema)), 0)

    slowk, _ = tools.stoch(high=h, low=l, close=c)
    self.assertGreater(len(list(slowk)), 0)

    adx = tools.adx(high=h, low=l, close=c)
    self.assertGreater(len(list(adx)), 0)

    mama, _ = tools.mesa(close=c)
    self.assertGreater(len(list(mama)), 0)
