import datetime
import os
import threading
from multiprocessing.pool import ThreadPool
from time import sleep

import tushare as ts

from utils import get_stock_basics


class History:
    today = None
    fail_pool = None
    mu = threading.Lock()
    repull = ['2017-03-02']

    def update_tick_and_dd(self, iterrow):
        index = iterrow[0]
        row = iterrow[1]
        print('update', index)

        try:
            time_to_market = str(row['timeToMarket'])
            start = '{}-{}-{}'.format(time_to_market[0:4], time_to_market[4:6], time_to_market[6:8])
            print(start)
            hist = ts.get_h_data(index, autype='None', start=start)
            # hist = ts.get_hist_data(index)
            if hist is None or len(hist) == 0:
                return

            root_path = 'd:/analyze_data'
            if not os.path.exists(root_path):
                os.makedirs(root_path)

            k_path = '{}/k'.format(root_path)
            if not os.path.exists(k_path):
                os.makedirs(k_path)

            hist.to_csv('{}/{}.csv'.format(k_path, index))

            tick_path = '{}/tick/{}'.format(root_path, index)
            if not os.path.exists(tick_path):
                os.makedirs(tick_path)

            # tick数据
            for i, row in hist.iterrows():
                date = str(i)[:10]

                if date == self.today:
                    continue

                filename = '{}/{}.csv'.format(tick_path, date)
                if not os.path.exists(filename):
                    print(filename)
                    tick = ts.get_tick_data(index, date=date)
                    tick.to_csv(filename)

            dd_path = '{}/dd/{}'.format(root_path, index)
            if not os.path.exists(dd_path):
                os.makedirs(dd_path)

            # 大单数据，貌似只有近十几个交易日的数据
            hist = hist.head(5)
            for i, row in hist.iterrows():
                date = str(i)[:10]

                if date == self.today:
                    continue

                filename = '{}/{}.csv'.format(dd_path, date)
                if not os.path.exists(filename):
                    print(filename)
                    dd = ts.get_sina_dd(index, date=date, vol=500)
                    if dd is not None:
                        dd.to_csv(filename)
        except Exception as e:
            self.mu.acquire()
            self.fail_pool.append(iterrow)
            self.mu.release()

            print(e)
            print('{} fail, put into fail pool'.format(index))

    def update(self):
        t = datetime.datetime.now()

        today = str(t.date())

        # redis_pool = redis.ConnectionPool(host='127.0.0.1', port='6379')

        basics = get_stock_basics()
        index_pool = list(basics.iterrows())
        self.fail_pool = []

        tp = ThreadPool()
        while len(index_pool) > 0:
            tp.map(self.update_tick_and_dd, index_pool)
            index_pool = self.fail_pool
            self.fail_pool = []
            sleep(5)

        print(datetime.datetime.now() - t)


if __name__ == '__main__':
    History().update()
