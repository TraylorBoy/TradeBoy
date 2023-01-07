"""Tests Client Modules"""

from tradeboy.client.proxy import Proxy
from phemexboy import PhemexBoy
from candleboy import CandleBoy

# Test params
FUTURE_SYMBOL = 'BTC/USD:USD'
SPOT_SYMBOL = 'sBTCUSDT'

client = Proxy(exchange='phemex', silent=False)


def test_init():
    global client

    assert 'phemex' in client.EXCHANGES
    assert isinstance(client._indicator_endpoint._client, CandleBoy)
    assert isinstance(client._auth_endpoint._client, PhemexBoy)
    assert isinstance(client._pub_endpoint._client, PhemexBoy)


def test_public():
    global client

    assert client.price(FUTURE_SYMBOL) > 0
    assert client.price(SPOT_SYMBOL) > 0

# Manual Tests Required For:
# - open_position
# - reopen_position


def test_auth():
    global client

    assert client.balance(of='USD', code='future') is not None
    assert client.balance(of='USDT', code='spot') is not None
    assert isinstance(client.in_position(FUTURE_SYMBOL), bool)


def test_indicator():
    global client

    macd, signal, history = client.macd(symbol=SPOT_SYMBOL, tf='1m')
    assert len(macd) > 0
    assert len(signal) > 0
    assert len(history) > 0

    params = {
        'fastperiod': 9,
        'slowperiod': 12,
        'signalperiod': 3
    }
    macd, signal, history = client.macd(
        symbol=FUTURE_SYMBOL, tf='1m', params=params)
    assert len(macd) > 0
    assert len(signal) > 0
    assert len(history) > 0

    ema = client.ema(symbol=SPOT_SYMBOL, tf='1m')
    assert len(ema) > 0

    params = {'timeperiod': 20}
    ema = client.ema(symbol=FUTURE_SYMBOL, tf='1m', params=params)
    assert len(ema) > 0


def test_all():
    test_init()
    test_public()
    test_auth()
    test_indicator()

    return True
