"""新浪大单"""
from multiprocessing.pool import ThreadPool

import tushare as ts


def get_dd(index):
    hist = ts.get_sina_dd(index, date='2017-02-06')
    print(hist)


if __name__ == '__main__':
    basics = ts.get_stock_basics()
    tp = ThreadPool()
    # tp.map(get_dd, basics.index)
    tp.map(get_dd, ['300268'])
