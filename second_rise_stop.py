'''二板'''
import datetime
import threading
from multiprocessing.pool import ThreadPool

import numpy as np

import tushare as ts


def explore_second_rise(index):
    global start, end, p, mu, sh

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
        if pChange[i - 3] > 9.5:  # 第一天涨停，则第三天不是二板
            continue
        if pChange[i - 2] <= 9.5 or pChange[i - 1] <= 9.5:  # 第二天第三天得是板
            continue
        if hist['high'][i - 1] == hist['low'][i - 1]:  # 第三天不能是一字板
            continue

        # TODO 检查是否放量

        # mssh0 = sh.get_value(hist.index[i - 3], 'ma5')
        # mssh1 = sh.get_value(hist.index[i - 2], 'ma5')
        # if mssh0 >= mssh1:  # 大盘上行
        #     continue

        # if ma5[i - 1] > ma10[i - 1] > ma20[i - 1]:
        #     if ma5[i - 0] > ma10[i - 0] > ma20[i - 0]:
        #         if ma5[i - 1] > ma5[i - 0] and ma10[i - 1] > ma10[i - 0] and ma20[i - 1] > ma20[i - 0]:

        # if ma10[i - 3] >= ma10[i - 2]:  # 个股上行
        #     continue

        mu.acquire()
        p.append(pChange[i])
        # p.append((hist['open'][i] - hist['close'][i - 1]) / hist['close'][i - 1] * 100)
        mu.release()


start = None
end = None

p = []
mu = threading.Lock()

sh = None

if __name__ == '__main__':
    s = datetime.datetime.now()

    global start, end, p, sh

    t = datetime.datetime.now() - datetime.timedelta(days=365 * 1 / 2)
    day = t.date()
    start = str(day)

    t = datetime.datetime.now() - datetime.timedelta(days=0 + 0)
    day = t.date()
    end = str(day)

    sh = ts.get_hist_data('sh')

    basics = ts.get_stock_basics()
    pool = ThreadPool()
    pool.map(explore_second_rise, basics.index)

    print(p)
    print('len', len(p))

    n = np.array(p)
    print((n > 0).sum())
    print((n <= 0).sum())
    print(n.mean())

    print('end')

    print(datetime.datetime.now() - s)
