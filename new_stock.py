# 新股开板
import datetime

import numpy as np
import tushare as ts


def get_new_stock_list():
    basics = ts.get_stock_basics()
    _filter = [row > 20160612 for row in basics['timeToMarket']]
    n_stocks = basics[_filter]
    diff = []
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
        diff.append((list(hist['close'])[1] - list(hist['high'])[0]) / list(hist['high'])[0])

    n = np.array(diff)
    print('开板新股数', len(n))
    print('上涨数', (n > 0).sum())
    print('下跌数', (n <= 0).sum())
    print('上涨概率', (n > 0).sum() / len(n))
    print('平均收益率', n.mean())


if __name__ == '__main__':
    s = datetime.datetime.now()
    get_new_stock_list()
    print(datetime.datetime.now() - s)
