"""General use functions"""

import datetime

from time import sleep

def sync():
    """Waits until the new minute starts"""
    t = datetime.datetime.utcnow()
    x = 60 - (t.second + t.microsecond/1000000.0)
    sleep(x)
