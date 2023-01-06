"""Example Future Strategy (No Exit)"""

from tradeboy import TradeBoy

# Strategy: 1m MACDEMA
# Long if price above 200 EMA and MACD crosses below 0
# Short if price below 200 EMA and MACD crosses above 0


class Strategy(TradeBoy):
    def __init__(self):
        # Set exchange
        super().__init__(exchange='phemex')
        # Required properties
        self.props = {
            'code': 'future',  # Or spot
            'symbol': 'BTC/USD:USD',  # Trading pair
            'tf': '1m'  # Timeframe
        }
        # Params needed to initiate trade
        self.params = {
            'type': 'limit',  # Or limit
            'side': None,  # long or short
            'amount': 5,  # How many contracts to trade with
            'tp': None,  # Take profit percent
            'sl': None  # Stop loss percent
        }

    def get_macd(self):
        # Get macd values
        # Use default params (12, 26, 9)
        macd, signal, _ = self.macd(
            symbol=self.props['symbol'], tf=self.props['tf'])
        # Format
        macd = list(macd)
        macd.reverse()
        signal = list(signal)
        signal.reverse()

        # Get current and previous values
        prev_macd = None
        last_macd = None
        prev_signal = None
        last_signal = None

        i = 0
        for value in macd:
            if str(value) != 'nan':
                prev_macd = macd[i + 1]
                last_macd = macd[i + 2]
                break
            i += 1

        i = 0
        for value in signal:
            if str(value) != 'nan':
                prev_signal = signal[i + 1]
                last_signal = signal[i + 2]
                break
            i += 1

        return prev_macd, last_macd, prev_signal, last_signal

    def get_ema(self):
        # Get ema value
        # Use default timeperiod = 200
        ema = self.ema(symbol=self.props['symbol'], tf=self.props['tf'])
        # Format
        ema = list(ema)
        ema.reverse()
        # Get current value
        curr_ema = None

        for value in ema:
            if str(value) != 'nan':
                curr_ema = value
                break

        return curr_ema

    def signal(self):
        # Get strategy params
        price = self.price(symbol=self.props['symbol'])
        prev_macd, last_macd, prev_signal, last_signal = self.get_macd()
        curr_ema = self.get_ema()
        # Debug
        """print(
            f'\nPREV_MACD: {prev_macd}\nPREV_SIGNAL: {prev_signal}\nLAST_MACD: {last_macd}\nLAST_SIGNAL: {last_signal}\nEMA: {curr_ema}\n')"""

        # Check for entry
        if price > curr_ema:
            # Look for long
            if last_macd < last_signal and prev_macd > prev_signal and prev_macd < 0 and prev_signal < 0:
                self.params['tp'] = 0.36  # 0.36%
                self.params['sl'] = 0.18  # 0.18%
                self.params['side'] = 'long'
                return True

        if price < curr_ema:
            # Look for short
            if last_macd > last_signal and prev_macd < prev_signal and prev_macd > 0 and prev_signal > 0:
                self.params['tp'] = 0.36
                self.params['sl'] = 0.18
                self.params['side'] = 'short'
                return True

        return False

    # Entry is required
    # Exit is not required if no tp/sl provided
    def entry(self):
        # Set strategy params
        # Returns True if signal was found
        # False if signal was not found
        return self.signal()

    # Exit conditions not needed for current strategy
    def exit(self):
        pass
