"""Tests the TradeBoy Module"""

from example import Strategy

from tradeboy import TradeBoy
client = TradeBoy(exchange='phemex')

# TODO: Test errors


def test_balance():
    global client

    spot_bal = client.balance(of='USDT', code='spot')
    future_bal = client.balance(of='USD', code='future')
    assert future_bal is not None and spot_bal is not None


def test_price():
    global client

    spot_price = client.price(symbol="sBTCUSDT")
    future_price = client.price(symbol='BTC/USD:USD')
    assert future_price > 0 and spot_price > 0


def test_macd():
    global client

    macd, signal, history = client.macd(symbol='BTCUSD', tf='1m')
    assert len(macd) > 0
    assert len(signal) > 0
    assert len(history) > 0

    params = {
        'fastperiod': 9,
        'slowperiod': 12,
        'signalperiod': 3
    }
    macd, signal, history = client.macd(
        symbol='BTCUSD', tf='1m', params=params)
    assert len(macd) > 0
    assert len(signal) > 0
    assert len(history) > 0


def test_ema():
    global client

    ema = client.ema(symbol='BTCUSD', tf='1m')
    assert len(ema) > 0

    params = {'timeperiod': 20}
    ema = client.ema(symbol='BTCUSD', tf='1m', params=params)
    assert len(ema) > 0


def test_position_status():
    global client

    pos = client.in_position(symbol='BTC/USD:USD')
    assert isinstance(pos, bool)


def test_percent():
    global client

    tp = client.profit_percent(
        symbol='BTC/USD:USD', percent=0.2, side='long')
    sl = client.loss_percent(
        symbol='BTC/USD:USD', percent=0.1, side='short')

    assert tp > 0 and sl > 0


def test_engine():
    global client

    client.engine(Strategy)


if __name__ == '__main__':
    # test_balance()
    # test_price()
    # test_macd()
    # test_ema()
    # test_position_status()
    # test_percent()
    test_engine()
    print('All tests passed')
