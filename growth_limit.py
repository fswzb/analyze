"""计算次日涨停价"""
import datetime
from multiprocessing.pool import ThreadPool

import numpy as np
import pandas as pd
import redis

import tushare as ts
from utils import get_stock_basics


def last_full_day():
    today = datetime.datetime.today()

    if today.hour < 16:
        t = datetime.datetime.now() - datetime.timedelta(days=1)
        day = t.date()
    else:
        day = today.date()

    return str(day)


def statistics():
    # hist = pd.read_csv('d:/quant/history/day/data/000001.csv')
    hist = pd.read_csv('d:/quant/history/day/data/002277.csv')
    print(hist)

    # 振幅
    zhenfu = (hist['high'] - hist['low']) / hist['open']
    print(zhenfu)

    hist['zhenfu'] = zhenfu
    print(hist)

    # 前一天的收盘价
    preclose = list(hist['close'])

    preclose.reverse()  # 倒置
    preclose.remove(preclose[0])  # 移除最近一天的
    preclose.append(preclose[len(preclose) - 1])  # 把第一天的收盘价再次插到第0位，第一天的涨幅就算它是0
    preclose.reverse()  # d倒置回来

    # 涨幅
    hist['growth'] = (hist['close'] - preclose) / preclose
    print(hist)

    hist['rise_stop'] = np.round(hist['growth'] * 100) / 10
    print(hist)

    # 涨停跌停次数
    print((hist['rise_stop'] == 1).sum())
    print((hist['rise_stop'] == -1).sum())


def set_rise_stop():
    hist = ts.get_hist_data()
    hist['rise_stop'] = np.int(hist['close'])


def get_next_rise_stop(hist):
    close = list(hist.tail(1)['close'])[0]
    rise_stop = round(close * 1.1, ndigits=2)
    return rise_stop


def get_rise_stop_count(hist):
    size = len(hist)
    if size < 4:
        return size

    hist = hist.tail(4)

    # 前一天的收盘价
    preclose = list(hist['close'])

    preclose.reverse()  # 倒置
    preclose.remove(preclose[0])  # 移除最近一天的
    preclose.append(preclose[len(preclose) - 1])  # 把第一天的收盘价再次插到第0位，第一天的涨幅就算它是0
    preclose.reverse()  # d倒置回来

    # 涨幅
    hist['growth'] = (hist['close'] - preclose) / preclose

    hist = hist.tail(3)

    hist['rise_stop'] = np.round(hist['growth'] * 100) / 10

    # 涨停次数
    return (hist['rise_stop'] == 1).sum()


def update_info(code):
    global end
    hist = ts.get_k_data(code, start='2015-01-01', end=end)

    if 'close' not in hist.keys():
        return
    if len(hist) == 0:
        return

    kv = {'quant.{}.rise_stop'.format(code): get_next_rise_stop(hist),
          'quant.{}.rise_stop_count'.format(code): get_rise_stop_count(hist)}

    r = redis.Redis(connection_pool=redis_pool)
    r.mset(kv)


redis_pool = None
end = last_full_day()

if __name__ == '__main__':
    global redis_pool

    s = datetime.datetime.now()

    redis_pool = redis.ConnectionPool(host='127.0.0.1', port='6379')
    r = redis.Redis(connection_pool=redis_pool)

    r.set('name', 'marz')
    print(r.get('name').decode('utf-8'))

    basics = get_stock_basics()
    tp = ThreadPool()
    tp.map(update_info, basics.index)

    print(datetime.datetime.now() - s)
