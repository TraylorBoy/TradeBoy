"""Automated Crypto Trader"""

import os

from candleboy import CandleBoy
from phemexboy import PhemexBoy
from dotenv import load_dotenv
load_dotenv()


class TradeBoy:
    def __init__(self, exchange):
        self.candleboy = CandleBoy()

        if exchange == "phemex":
            self.client = PhemexBoy(
                os.getenv('PHEMEX_KEY'), os.getenv('PHEMEX_SECRET'))

    def balance(self, of, code='spot'):
        """Retrieve balance from specific account

        of (String) - Asset to retrieve balance for
        code (String) - Values should be either spot or future to indicate which
        account to retrieve balance for (default is swap due to not every
        exchange having a future option)
        """
        bal = None

        if code == 'spot':
            bal = self.client.balance(of)
        elif code == 'future':
            bal = self.client.future_balance(of)
        else:
            raise Exception('Invalid code')

        return bal
