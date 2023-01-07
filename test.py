"""Tests the TradeBoy Package"""

from tests import test_client, test_helpers
from tradeboy.engine import Engine
from strategies.example import Strategy

engine = Engine(exchange='phemex', silent=False)

if __name__ == '__main__':
    test = int(input('Number: '))
    if test == 1 and not test_client.test_all():
        print('Client test failed')
    if test == 2 and not test_helpers.test_all():
        print('Helpers test failed')
    if test == 3:
        print('\nTHIS WILL MANUALLY TEST THE ENGINE BY RUNNING THE EXAMPLE STRATEGY ON THE FUTURE MARKET AND USE REAL FUNDS\n')
        engine.run(Strategy)
    print('All tests passed')
