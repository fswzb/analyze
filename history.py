import datetime
import os
from multiprocessing.pool import ThreadPool

import redis

import tushare as ts


def update(index):
    print('update', index)

    # hist = ts.get_h_data(index)
    hist = ts.get_hist_data(index)

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

        tick = ts.get_tick_data(index, date=date)
        # r.set(key, tick.to_string())
        tick.to_csv(filename)


redis_pool = None
if __name__ == '__main__':
    t = datetime.datetime.now()

    redis_pool = redis.ConnectionPool(host='127.0.0.1', port='6379')

    basics = ts.get_stock_basics()
    tp = ThreadPool()
    tp.map(update, basics.index)

    print(datetime.datetime.now() - t)
