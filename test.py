"""Tests the TradeBoy Module"""

from tradeboy import TradeBoy

client = TradeBoy(exchange='phemex')


def test_balance():
    global client

    bal = client.balance(of='USD', code='future')
    print(bal)
    assert bal is not None


if __name__ == '__main__':
    test_balance()

    print('All tests passed')
