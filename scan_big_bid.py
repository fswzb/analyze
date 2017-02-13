"""大单扫货到，使股价达到涨停"""
import datetime
import os
import threading
from datetime import time
from multiprocessing.pool import ThreadPool

import pandas as pd
import redis

import tushare as ts
from easyutils import get_stock_type
from utils import get_stock_basics


def get_bid(index):
    if index in codes:
        return

    hist = ts.get_sina_dd(index, date=date, vol=500)
    if hist is not None:
        # print(index, hist['volume'].sum())

        hist = hist.iloc[::-1]
        r = redis.Redis(connection_pool=redis_pool)
        rise_stop = r.get('quant.{}.rise_stop'.format(index))
        rise_stop = float(rise_stop)
        super_dd = False
        for i in range(len(hist)):
            if hist['volume'][i] > 2000 * 100:
                super_dd = True

            if hist['price'][i] == rise_stop:  # 涨停
                if hist['preprice'][i] != 0:  # 开盘涨停
                    # if hist['preprice'][i] != hist['price'][i] or super_dd:  # 大单打到涨停
                    if hist['preprice'][i] != hist['price'][i]:  # 大单打到涨停
                        mu.acquire()
                        codes.append(index)
                        mu.release()
                        print('time: {}, rise stop: {}, preprice: {}, price: {}'.format(hist['time'][i], rise_stop,
                                                                                        hist['preprice'][i],
                                                                                        hist['price'][i]))
                        print('https://xueqiu.com/S/{}{}'.format(get_stock_type(index).upper(), index))
                        break


date = None
redis_pool = None
codes = []
mu = threading.Lock()
if __name__ == '__main__':
    t = datetime.datetime.now()

    date = t.date()
    date = str(date)
    # date = '2017-02-09'

    redis_pool = redis.ConnectionPool(host='127.0.0.1', port='6379')

    basics = get_stock_basics()
    basics = basics[basics['outstanding'] < 5]
    print('关注{}只股票'.format(len(basics)))

    close_time = time(hour=15)
    i = 0
    tp = ThreadPool()
    keep_scan = True
    while keep_scan:
        i += 1
        print('round', i)

        now = datetime.datetime.now()
        if now.time() > close_time:
            keep_scan = False

        try:
            tp.map(get_bid, basics.index)
        except:
            pass

        end_time = datetime.datetime.now()
        print('round {}, curent time {}, elapsed time: {}'.format(i, end_time.time(), end_time - now))

    print('codes', codes)

    all = ts.get_today_all()
    all_index = list(all['code'])

    filterd = pd.DataFrame()
    for i in codes:
        index = all_index.index(i)
        row = all.loc[index]
        row['url'] = 'https://xueqiu.com/S/{}{}'.format(get_stock_type(i).upper(), i)
        filterd = filterd.append(row)

    now = pd.DataFrame({'code': filterd['code']})
    now['name'] = filterd['name']
    now['high'] = filterd['high']
    now['close'] = (100 + filterd['changepercent']) * filterd['settlement'] / 100
    now['highpercent'] = ((now['close'] - filterd['high']) / filterd['high'] * 100).round(3)
    now['url'] = filterd['url']
    now = now.reset_index(drop=True)
    now = now.sort_values('highpercent')

    path = 'data/scan_big_bid'
    if not os.path.exists(path):
        os.makedirs(path)
    now.to_csv('{}/{}.csv'.format(path, date))

    negative = (now['highpercent'] == 0).sum() / len(now) * 100
    avg = now['highpercent'].mean()

    print(now)
    print('封板率：{}%'.format(round(negative, 2)))
    print('打板当日收益率：{}%'.format(round(avg, 2)))

    print(datetime.datetime.now() - t)
