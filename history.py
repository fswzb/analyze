import datetime
import os
from multiprocessing.pool import ThreadPool

import redis
import tushare as ts


def update(index):
    print('update', index)

    # hist = ts.get_h_data(index)
    hist = ts.get_hist_data(index)

    path = 'd:/analyze_data'
    if not os.path.exists(path):
        os.mkdir(path)

    hist.to_csv('{}/{}.csv'.format(path, index))

    r = redis.Redis(connection_pool=redis_pool)
    for i, row in hist.iterrows():
        date = str(i)
        key = '{}_{}'.format(index, date)

        if r.exists(key):
            continue

        print(key)
        tick = ts.get_tick_data(index, date=date)
        r.set(key, tick.to_string())


redis_pool = None
if __name__ == '__main__':
    t = datetime.datetime.now()

    redis_pool = redis.ConnectionPool(host='127.0.0.1', port='6379')

    basics = ts.get_stock_basics()
    tp = ThreadPool()
    tp.map(update, basics.index)

    print(datetime.datetime.now() - t)
