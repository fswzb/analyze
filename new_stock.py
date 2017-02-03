'''新股开板战法'''
import datetime

import numpy as np

import tushare as ts


def get_new_stock_list():
    '''
    第二天的收盘价 - 第一天的最高价
    开板新股数 167
    上涨数 45
    下跌数 122
    上涨概率: 26.95%
    平均收益率: -4.62%

    第二天的开盘价 - 第一天的开盘价
    开板新股数 167
    上涨数 55
    下跌数 112
    上涨概率: 32.93%
    平均收益率: -2.94%

    第二天的开盘价 - 第一天的最高和最低的中间价
    开板新股数 167
    上涨数 65
    下跌数 102
    上涨概率: 38.92%
    平均收益率: -1.33%

    第二天的最高和最低的中间价 - 第一天的最高和最低的中间价
    开板新股数 167
    上涨数 74
    下跌数 93
    上涨概率: 44.31%
    平均收益率: -0.64%

    第二天的收盘价 - 第一天的收盘价
    开板新股数 167
    上涨数 64
    下跌数 103
    上涨概率: 38.32%
    平均收益率: -0.99%
    '''

    basics = ts.get_stock_basics()
    _filter = [row > 20160612 for row in basics['timeToMarket']]
    n_stocks = basics[_filter]
    strategy1 = []
    strategy2 = []
    strategy3 = []
    strategy4 = []
    strategy5 = []
    for index in n_stocks.index:
        hist = ts.get_k_data(index)
        hist = hist.tail(len(hist) - 1)
        hist['rise_stop_open'] = hist['high'] != hist['low']
        _filter = list(hist['rise_stop_open'])
        hist = hist[_filter]

        _len = len(hist)

        if _len < 2:
            continue

        # 第二天的收盘价 - 第一天的最高价，算是收益，然后计算收益率
        strategy1.append((list(hist['close'])[1] - list(hist['high'])[0]) / list(hist['high'])[0])
        # 第二天的开盘价 - 第一天的开盘价，算是收益，然后计算收益率
        strategy2.append((list(hist['open'])[1] - list(hist['open'])[0]) / list(hist['open'])[0])

        b_price = (list(hist['high'])[0] + list(hist['low'])[0]) / 2
        strategy3.append((list(hist['open'])[1] - b_price) / b_price)

        s_price = (list(hist['high'])[1] + list(hist['low'])[1]) / 2
        strategy4.append((s_price - b_price) / b_price)

        strategy5.append((list(hist['close'])[1] - list(hist['close'])[0]) / list(hist['close'])[0])

    print('第二天的收盘价 - 第一天的最高价')
    print_info(np.array(strategy1))

    print('第二天的开盘价 - 第一天的开盘价')
    print_info(np.array(strategy2))

    print('第二天的开盘价 - 第一天的最高和最低的中间价')
    print_info(np.array(strategy3))

    print('第二天的最高和最低的中间价 - 第一天的最高和最低的中间价')
    print_info(np.array(strategy4))

    print('第二天的收盘价 - 第一天的收盘价')
    print_info(np.array(strategy5))


def print_info(n):
    print('开板新股数', len(n))
    print('上涨数', (n > 0).sum())
    print('下跌数', (n <= 0).sum())
    print('上涨概率: {}%'.format(round((n > 0).sum() / len(n) * 100, ndigits=2)))
    print('平均收益率: {}%'.format(round(n.mean() * 100, ndigits=2)))
    print()


if __name__ == '__main__':
    s = datetime.datetime.now()
    get_new_stock_list()
    print(datetime.datetime.now() - s)
