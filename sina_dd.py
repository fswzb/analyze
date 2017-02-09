"""新浪大单"""
import datetime
from multiprocessing.pool import ThreadPool

import tushare as ts


def get_dd(index):
    hist = ts.get_sina_dd(index, date=date, vol=500)
    print(hist)
    print(hist['volume'].sum())
    buy = hist[hist['type'].str.contains('买盘')]['volume'].sum()
    sell = hist[hist['type'].str.contains('卖盘')]['volume'].sum()
    print('买盘', buy)
    print('卖盘', sell)
    print(round(buy / sell, 2))


date = None
if __name__ == '__main__':
    t = datetime.datetime.now()

    date = datetime.datetime.now().date()
    date = str(date)
    # basics = ts.get_stock_basics()
    tp = ThreadPool()
    # tp.map(get_dd, basics.index)
    tp.map(get_dd, ['002825'])

    print(datetime.datetime.now() - t)
