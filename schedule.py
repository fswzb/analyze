import datetime
import time
from enum import Enum

import pandas as pd
import redis
from apscheduler.schedulers.blocking import BlockingScheduler

import easytrader
import tushare as ts
from bbi_strategy import get_bbi_match_2
from history import History
from history_day import update_day


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
        print(dt)
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

        now = datetime.datetime.now()
        code = get_bbi_match_2(str(now.date()))

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

        history = History()

        sched = BlockingScheduler()
        sched.add_job(self.reset, 'cron', day_of_week='0-4', hour='9', second='0')
        sched.add_job(self.buy, 'cron', day_of_week='0-4', hour='9', minute='30')

        # 半点 9:30:00~9:59:59
        sched.add_job(self.tick, 'cron', day_of_week='0-4', hour='9', minute='30-59', second='*/5')
        # 半点 11:00:00~11:30:59
        sched.add_job(self.tick, 'cron', day_of_week='0-4', hour='11', minute='0-30', second='*/5')
        # 整点 10:00:00~10:59:59 13:00:00~14:59:59
        sched.add_job(self.tick, 'cron', day_of_week='0-4', hour='10,13-14', second='*/5')

        sched.add_job(history.update, 'cron', day_of_week='0-4', hour='15', minute='30')
        sched.add_job(self.select, 'cron', day_of_week='0-4', hour='16')

        sched.add_job(self.buy, 'cron', day_of_week='0-4', hour='14', minute='20')
        sched.add_job(self.sell, 'cron', day_of_week='0-4', hour='14', minute='20')

        sched.add_job(update_day, 'cron', day_of_week='0-4', hour='23', minute='0')

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
