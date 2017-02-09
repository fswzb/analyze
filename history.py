import datetime
import os
import threading
from multiprocessing.pool import ThreadPool
from time import sleep

import tushare as ts


def update(index):
    print('update', index)

    try:
        # hist = ts.get_h_data(index)
        hist = ts.get_hist_data(index)
        if hist is None or len(hist) == 0:
            return

        root_path = 'd:/analyze_data'
        if not os.path.exists(root_path):
            os.makedirs(root_path)

        k_path = '{}/k'.format(root_path)
        if not os.path.exists(k_path):
            os.makedirs(k_path)

        hist.to_csv('{}/{}.csv'.format(k_path, index))

        # r = redis.Redis(connection_pool=redis_pool)

        tick_path = '{}/tick/{}'.format(root_path, index)
        if not os.path.exists(tick_path):
            os.makedirs(tick_path)

        for i, row in hist.iterrows():
            date = str(i)
            # key = '{}_{}'.format(index, date)

            # if r.exists(key):
            #     continue

            # print(key)

            filename = '{}/{}.csv'.format(tick_path, date)
            if os.path.exists(filename):
                continue

            print(filename)
            tick = ts.get_tick_data(index, date=date)
            # r.set(key, tick.to_string())
            tick.to_csv(filename)
    except:
        mu.acquire()
        fail_pool.append(index)
        mu.release()

        print('{} fail, put into fail pool'.format(index))


# redis_pool = None
fail_pool = []
mu = threading.Lock()
if __name__ == '__main__':
    t = datetime.datetime.now()

    # redis_pool = redis.ConnectionPool(host='127.0.0.1', port='6379')

    basics = ts.get_stock_basics()
    index_pool = basics.index

    tp = ThreadPool()
    while len(index_pool) > 0:
        tp.map(update, index_pool)
        index_pool = fail_pool
        fail_pool = []
        sleep(5)

    print(datetime.datetime.now() - t)
