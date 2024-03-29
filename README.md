# TradeBoy
Automated crypto trader

## Notes
- Only exchange is Phemex so far
- Only future engine works
  - exit condition not in yet

## Installation
- Requires TA-Lib which may be difficult to install
- Here is their install docs https://mrjbq7.github.io/ta-lib/install.html

```
pip install tradeboy
```

## Usage
### Instantiation
- Requires .env with API credentials
- Engine handles placing orders
- Strategy sends engine entry signals
  - exit signals not required if tp/sl percents provided in params
- Can add Discord webhook to have logs sent to a server if verbose is set to True
```
from tradeboy.engines.future import FutureEngine
from strategies.example import Strategy as ex_strat

# Rate is request rate
# Runs example strategy in strategies folder
engine = FutureEngine(Strategy=ex_strat, rate=30, verbose=True, webhook=None)
engine.run(trades=100)
```

### Example Strategy
- Requires self.params in order to inititate the trade
- Requires ```entry``` method
  - ```exit``` only required if not using take profit or stop loss
```
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
```

### Tools helper class
```
from tradeboy.tools import Tools

# Strategy class init
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

# Create trading symbol for params
self.tools.symbol(base='BTC', quote='USD', code='future'), # Trading pair

# Get open-high-low-close-volume data
timestamps, open, high, low, close, volume = self.tools.ohlcv(symbol=self.params['symbol'], tf='1m')

# Get macd
_, _, _, _, close, _ = self.tools.ohlcv(symbol=self.params['symbol'], tf='1m')
macd, signal, history = self.tools.macd(close)

# Get ema
_, _, _, _, close, _ = self.tools.ohlcv(symbol=self.params['symbol'], tf='1m')
ema = self.tools.ema(close)

# Get stoch
_, _, high, low, close, _ = self.tools.ohlcv(symbol=self.params['symbol'], tf='1m')
slowk, slowd = self.tools.stoch(high, low, close)

# Get adx
_, _, high, low, close, _ = self.tools.ohlcv(symbol=self.params['symbol'], tf='1m')
adx = self.tools.adx(high, low, close)

# Get mesa
_, _, _, _, close, _ = self.tools.ohlcv(symbol=self.params['symbol'], tf='1m')
mama, fama = self.tools.mesa(close)

# Get price
price = self.tools.price(symbol=self.params['symbol'])
```

## Test

- Runs the example strategy

```
make test
```
