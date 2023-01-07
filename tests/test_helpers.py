"""Tests Helper Modules"""

import tradeboy.helpers.calc as calc

from tradeboy.helpers.info import Info
from tradeboy.helpers.stats import Stats
from tradeboy.client.proxy import Proxy


class Test_Strategy:
    def __init__(self):
        self.props = {
            'code': 'future',  # Or spot
            'symbol': 'BTC/USD:USD',  # Trading pair
            'tf': '1m'  # Timeframe
        }
        # Params needed to initiate trade
        self.params = {
            'type': 'limit',  # Or limit
            'side': 'long',  # long or short
            'amount': 5,  # How many contracts to trade with
            'tp': 2,  # Take profit percent
            'sl': 1  # Stop loss percent
        }


proxy = Proxy('phemex', silent=False)
info = Info(proxy)
strategy = Test_Strategy()
stats = Stats(proxy)


def test_info():
    global info, strategy

    info.collect(strategy)
    for x in list(strategy.props.keys()):
        assert x in list(info.data.keys())
    for x in list(strategy.params.keys()):
        assert x in list(info.data.keys())

    info.update_targets(3, 4)
    assert info.data['tp'] == 3 and info.data['sl'] == 4

    # Test __str__
    print(info)


def test_stats():
    global stats, info

    stats.update(info)
    assert stats.data['trades'] == 1
    assert stats.data['profit'] == 0
    assert stats.data['wins'] == 0
    assert stats.data['losses'] == 0

    # Test __str__
    print(stats)


def test_calc():
    price = 10000
    percent = 10

    assert calc.tp(percent, 'long', price) == 11000
    assert calc.tp(percent, 'short', price) == 9000
    assert calc.sl(percent, 'long', price) == 9000
    assert calc.sl(percent, 'short', price) == 11000


def test_all():
    test_info()
    test_stats()
    test_calc()

    return True
