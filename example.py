"""Example Future Strategy"""

from tradeboy import TradeBoy


class Strategy(TradeBoy):
    def __init__(self):
        # Set exchange
        super().__init__(exchange='phemex')
        # Set strategy market
        self.code = 'future'
        # Set trading pair
        self.symbol = 'BTC/USD:USD'

    def entry(self):
        params = {}

        # Get current price
        price = self.price(symbol=self.symbol)
        print(f'Retrieved current price: {price}')
        # Get macd values
        # Use default params (12, 26, 9)
        macd, signal, _ = self.macd(symbol=self.symbol, tf='1m')
        # Get current values
        curr_macd = None
        curr_signal = None

        for value in macd:
            print(value)

    def exit(self):
        pass
