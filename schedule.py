import datetime
import sched
import time
from enum import Enum

import easytrader
import pandas as pd
import redis
import tushare as ts


class TradingState(Enum):
    before = 0
    open = 1
    closed = 2


class Strategy:
    schedule = sched.scheduler(time.time, time.sleep)
    trading_state = TradingState.closed
    redis_poll = redis.ConnectionPool(host='127.0.0.1', port='6379')
    redis_conn = redis.Redis(connection_pool=redis_poll)
    user = None

    def __init__(self):
        self.user = easytrader.use('yh')
        self.user.prepare('../easytrader/yh.json')

        print('position', self.user.position)
        print('entrust', self.user.entrust)
        print('balance', self.user.balance)

    def update(self, dt):
        today = str(dt.date())
        trade_cal = ts.trade_cal()
        trade_cal['calendarDate'] = pd.to_datetime(trade_cal['calendarDate'])
        trade_cal = trade_cal.set_index('calendarDate')
        if trade_cal.loc[today]['isOpen'] == 0:
            return

        now_delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute)
        open_delta = datetime.timedelta(hours=9, minutes=30)
        close_delta = datetime.timedelta(hours=15, minutes=0)
        if not (open_delta < now_delta < close_delta):
            print('not open')
        else:
            print('opened')

    def tick(self):
        pass

    def select(self):
        self.redis_conn.set('bbi_select', '')

    def buy(self):
        self.redis_conn.set('bbi', '')

    def sell(self):

        self.redis_conn.delete('bbi')

    def reset(self):
        trading_state = TradingState.closed

    def start(self):
        while True:
            now = datetime.datetime.now()

            try:
                self.update(now)
            except Exception as e:
                print(e)

            elapsed = datetime.datetime.now() - now

            diff = 5 - elapsed.total_seconds()
            if diff > 0:
                time.sleep(diff)


if __name__ == '__main__':
    Strategy().start()
