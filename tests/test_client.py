"""Tests Helper Client Module"""

from helpers.client import Client
from phemexboy import PhemexBoy
from candleboy import CandleBoy
# TODO: Test errors

# Test params
FUTURE_SYMBOL = 'BTC/USD:USD'
SPOT_SYMBOL = 'sBTCUSDT'

client = Client(exchange='phemex', silent=False)


def test_init():
    global client

    assert 'phemex' in client.EXCHANGES
    assert client._silent is False
    assert isinstance(client._indicator._client, CandleBoy)
    assert isinstance(client._auth_endpoint._client, PhemexBoy)
    assert isinstance(client._pub_endpoint._client, PhemexBoy)


def test_public():
    global client

    assert client.price(FUTURE_SYMBOL) > 0
    assert client.price(SPOT_SYMBOL) > 0


def test_auth():
    global client

    assert client.balance(of='USD', code='future') is not None
    assert client.balance(of='USDT', code='swap') is not None


def test_errors():
    pass


def test_all():
    test_init()
    test_public()

    return True
