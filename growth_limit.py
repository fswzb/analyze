# 涨停
import os

import numpy as np
import pandas as pd
import redis


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


def round_to_cent(price):
    return int(round(price * 100)) / 100


def get_next_rise_stop(hist):
    close = list(hist.tail(1)['close'])[0]
    rise_stop = round_to_cent(round_to_cent(close) * 1.1)
    return rise_stop


def get_rise_stop_count(hist):
    size = len(list(hist['close']))
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


if __name__ == '__main__':
    pool = redis.ConnectionPool(host='127.0.0.1', port='6379')
    r = redis.Redis(connection_pool=pool)

    r.set('name', 'marz')
    print(r.get('name').decode('utf-8'))

    lst = os.listdir(u'D:\quant\history\day\data')
    print(lst)

    index = 0;
    batch_count = 50
    kv = {}
    for x in lst:
        index += 1
        code = x[0:6]
        hist = pd.read_csv('d:/quant/history/day/data/{}.csv'.format(code))
        kv['quant.{}.rise_stop'.format(code)] = get_next_rise_stop(hist)
        kv['quant.{}.rise_stop_count'.format(code)] = get_rise_stop_count(hist)

        if index % batch_count == batch_count - 1:
            r.mset(kv)
            print(kv)
            kv = {}

    r.mset(kv)
    print(kv)
    kv = {}
