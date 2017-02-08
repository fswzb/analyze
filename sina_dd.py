"""新浪大单"""
import datetime
from multiprocessing.pool import ThreadPool

import tushare as ts


def get_dd(index):
    hist = ts.get_sina_dd(index, date=date, vol=500)
    # print(hist)
    print(hist['volume'].sum())


date = None
if __name__ == '__main__':
    t = datetime.datetime.now()

    date = datetime.datetime.now().date()
    date = str(date)
    # basics = ts.get_stock_basics()
    tp = ThreadPool()
    # tp.map(get_dd, basics.index)
    # tp.map(get_dd, ['300268'])
    # tp.map(get_dd, ['002591'])
    # tp.map(get_dd, ['300323'])
    tp.map(get_dd, ['601177'])
    # tp.map(get_dd, ['002552'])

    print(datetime.datetime.now() - t)
