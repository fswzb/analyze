"""收在五日均线下出局"""
import datetime
import threading
from multiprocessing.pool import ThreadPool

import numpy as np

import tushare as ts
from utils import get_stock_basics


def explore_second_rise(index):
    global start, end, p_change_array, mu

    hist = ts.get_hist_data(index, start=start, end=end)

    if hist is None:
        return

    _len = len(hist)
    if _len < 4:  # 第一天用来计算第三天是否是二板，第四天计算收益
        return

    hist = hist.iloc[::-1]
    # print(hist)

    pChange = hist['p_change']
    ma5 = hist['ma5']
    ma10 = hist['ma10']
    ma20 = hist['ma20']

    for i in range(2, _len):
        if pChange[i - 3] > 9.5:  # 第一天不能涨停，否则第三天不是二板
            continue
        if pChange[i - 2] <= 9.5 or pChange[i - 1] <= 9.5:  # 第二天第三天得是板
            continue
        if hist['high'][i - 1] == hist['low'][i - 1]:  # 第三天不能是一字板
            continue

        buy_price = hist['open'][i - 1]
        sell_price = hist['close'][i]

        offset = 0
        while True:
            if i + offset >= _len:
                break

            sell_price = hist['close'][i + offset]

            if hist['close'][i + offset] < hist['ma5'][i + offset]:
                offset += 1
                break

            offset += 1

        mu.acquire()
        # p.append((sell_price - buy_price) / buy_price / offset * 100)
        p_change_array.append((sell_price - buy_price) / buy_price * 100)
        mu.release()


start = None
end = None

p_change_array = []
mu = threading.Lock()

if __name__ == '__main__':
    s = datetime.datetime.now()

    global start, end, p_change_array

    t = datetime.datetime.now() - datetime.timedelta(days=365 * 1 / 2)
    day = t.date()
    start = str(day)

    t = datetime.datetime.now() - datetime.timedelta(days=0 + 0)
    day = t.date()
    end = str(day)

    basics = get_stock_basics()
    pool = ThreadPool()
    pool.map(explore_second_rise, basics.index)

    print(p_change_array)
    print('len', len(p_change_array))

    n = np.array(p_change_array)
    print((n > 0).sum())
    print((n <= 0).sum())
    print(n.mean())

    print('end')

    print(datetime.datetime.now() - s)
