"""Engine calculation helpers"""


def tp(percent, side, price):
    """Calculates take profit price based off of percentage from current price

    percent (Integer) - Percent to calculate profit price
    side (String) - What side of the trade you are on (ex. long, short, buy, sell)
    price (Double) - Current price
    """
    if side == 'long':
        return price + (price * (percent / 100))
    if side == 'short':
        return price - (price * (percent / 100))


def sl(percent, side, price):
    """Calculates stop loss price based off of percentage from current price

    percent (Integer) - Percent to calculate stop loss price
    side (String) - What side of the trade you are on (ex. long, short, buy, sell)
    price (Double) - Current price
    """
    if side == 'long':
        return price - (price * (percent / 100))
    if side == 'short':
        return price + (price * (percent / 100))
