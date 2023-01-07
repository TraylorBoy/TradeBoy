"""Engine stats"""


class Stats:
    def __init__(self, proxy):
        self.data = {'wins': 0, 'losses': 0, 'profit': 0, 'trades': 0}
        # Authenticated Client
        self._proxy = proxy

    def __str__(self):
        wins = self.data['wins']
        losses = self.data['losses']
        trades = self.data['trades']
        profit = round(self.data['profit'], 2)

        return f'\nStats\n-------\nWins: {wins}\nLosses: {losses}\nProfit: {profit} (USD)\nTrades: {trades}\n'

    def update(self, info):
        """Updates profit and trades

        info (Info) - Instantiated info object that has collected params and props
        """
        try:
            if 'code' not in info.data and 'balance' not in info.data:
                raise Exception(
                    'Info object must collect strategy params and props first')

            code = info.data['code']
            bal_before = info.data['balance']
            bal = self._proxy.balance('USD', code)

            self.data['profit'] += bal - bal_before
            self.data['trades'] += 1

            if bal_before < bal:
                self.data['wins'] += 1
            if bal_before > bal:
                self.data['losses'] += 1
        except Exception as e:
            print(e)
            raise Exception('Failed to update stats')
