"""Strategy params and props"""


class Info:
    def __init__(self, proxy):
        self.data = {'balance': None}
        # Authenticated proxy client
        self._proxy = proxy

    def __str__(self):
        self.update_balance()
        side = self.data['side']
        symbol = self.data['symbol']
        amount = self.data['amount']
        code = self.data['code']
        type = self.data['type']
        sl = round(self.data['sl'], 2)
        tp = round(self.data['tp'], 2)
        balance = round(self.data['balance'], 2)

        return f'\nInformation\n----------\nMarket: {code}\nSide: {side}\nOrder Type: {type}\nBalance: ${balance}\nSymbol: {symbol}\nTP: ${tp}\nSL: ${sl}\nAmount: {amount}'

    def update_balance(self):
        """Updates the balance param"""
        try:
            self.data['balance'] = self._proxy.balance(
                'USD', self.data['code'])
        except Exception as e:
            print(e)
            raise Exception('Failed to update balance')

    def update_targets(self, tp, sl):
        """Update tp and sl price targets"""
        self.data['tp'] = tp
        self.data['sl'] = sl

    def collect(self, strategy):
        """Collect strategy params and props"""
        self.data.update(strategy.props)
        self.data.update(strategy.params)
        self.update_balance()
