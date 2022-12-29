"""Tests the TradeBoy Module"""

from example import Strategy

from tradeboy import TradeBoy

client = TradeBoy(exchange='phemex')


def test_balance():
    global client

    bal = client.balance(of='USD', code='future')
    print(bal)
    assert bal is not None


def test_engine():
    global client

    client.engine(Strategy)


if __name__ == '__main__':
    test_balance()
    test_engine()
    print('All tests passed')
