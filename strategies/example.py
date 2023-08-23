"""Example Future Strategy (No Exit)"""

# Strategy: 1m MACDEMA
# Long if price above 200 EMA and MACD crosses below 0
# Short if price below 200 EMA and MACD crosses above 0

from tradeboy.tools import Tools

class Strategy:
    def __init__(self):
        # Helper class
        self.tools = Tools(exchange='phemex', verbose=False)
        # Required params needed to initiate trade
        self.params = {
            'type': 'market',  # Or limit
            'side': None,  # long or short
            'amount': 1,  # How many contracts to trade with
            'tp_percent': None,  # Take profit percent
            'sl_percent': None,  # Stop loss percent
            'symbol': self.tools.symbol(base='BTC', quote='USD', code='future'), # Trading pair,
            'exit': False # Exit signal
        }

    def get_macd(self):
        # Get macd values
        # Use default params (12, 26, 9)
        _, _, _, _, close, _ = self.tools.ohlcv(symbol=self.params['symbol'], tf='1m')
        macd, signal, _ = self.tools.macd(close)
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
        _, _, _, _, close, _ = self.tools.ohlcv(symbol=self.params['symbol'], tf='1m')
        ema = self.tools.ema(close)

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
        price = self.tools.price(symbol=self.params['symbol'])
        prev_macd, last_macd, prev_signal, last_signal = self.get_macd()
        curr_ema = self.get_ema()

        # Check for entry
        if price > curr_ema:
            # Look for long
            if last_macd < last_signal and prev_macd > prev_signal and prev_macd < 0 and prev_signal < 0:
                self.params['tp_percent'] = 0.36  # 0.36%
                self.params['sl_percent'] = 0.18  # 0.18%
                self.params['side'] = 'long'
                return True

        if price < curr_ema:
            # Look for short
            if last_macd > last_signal and prev_macd < prev_signal and prev_macd > 0 and prev_signal > 0:
                self.params['tp_percent'] = 0.36
                self.params['sl_percent'] = 0.18
                self.params['side'] = 'short'
                return True

        return False

    # Entry is required
    # Exit is not required if no tp/sl provided
    def entry(self):
        # Returns True if signal was found
        # False if signal was not found
        return self.signal()

    # Exit conditions not needed for current strategy
    def exit(self):
        pass
