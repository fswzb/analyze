import datetime
import time
from enum import Enum

import easytrader
import pandas as pd
import redis
import tushare as ts
from apscheduler.schedulers.blocking import BlockingScheduler

from bbi_strategy import get_bbi_match


class TradingState(Enum):
    before = 0
    open = 1
    closed = 2


class Strategy:
    trading_state = TradingState.closed
    redis_poll = redis.ConnectionPool(host='127.0.0.1', port='6379')
    redis_conn = redis.Redis(connection_pool=redis_poll)
    user = None
    hold_days = 17

    def __init__(self):
        self.user = easytrader.use('yh')
        self.user.prepare('../easytrader/yh.json')

        print('position', self.user.position)
        print('entrust', self.user.entrust)
        print('balance', self.user.balance)

        self.sell()

    def tick(self):
        dt = datetime.datetime.now()
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

    def select(self):
        positions = self.user.position
        if len(positions) > 0:  # 持仓中
            return

        code = get_bbi_match()

        if code is not None:
            self.redis_conn.set('bbi_select', code)  # 存入选中的股票

    def buy(self):
        self.redis_conn.set('bbi', '')
        print('buy')

    def sell(self):
        while True:
            positions = self.user.position
            if len(positions) == 0:
                break

            self.user.cancel_entrusts('')
            self.user.sell('600423', 60, entrust_prop='market')
            self.redis_conn.delete('bbi')

            time.sleep(30)

    def reset(self):
        trading_state = TradingState.closed

    def start(self):

        sched = BlockingScheduler()
        sched.add_job(self.reset, 'cron', second='0', day_of_week='0-4', hour='9')
        sched.add_job(self.buy, 'cron', minute='30', day_of_week='0-4', hour='9')
        sched.add_job(self.tick, 'cron', second='*/5', day_of_week='0-4', hour='9-12,13-15')
        sched.add_job(self.select, 'cron', day_of_week='0-4', hour='16')

        sched.add_job(self.buy, 'cron', minute='20', day_of_week='0-4', hour='14')
        sched.add_job(self.sell, 'cron', minute='20', day_of_week='0-4', hour='14')

        try:
            sched.start()
        except Exception as e:
            print(e)

        # while True:
        #     now = datetime.datetime.now()
        #
        #     try:
        #         self.tick(now)
        #     except Exception as e:
        #         print(e)
        #
        #     elapsed = datetime.datetime.now() - now
        #
        #     diff = 5 - elapsed.total_seconds()
        #     if diff > 0:
        #         time.sleep(diff)
        print('end')


if __name__ == '__main__':
    Strategy().start()
