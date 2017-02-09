"""大单扫货到，使股价达到涨停"""
import datetime
from multiprocessing.pool import ThreadPool

import pandas as pd
import tushare as ts


def get_bid(index):
    hist = ts.get_sina_dd(index, date=date, vol=500)
    if hist is not None:
        print(index, hist['volume'].sum())


date = None
if __name__ == '__main__':
    t = datetime.datetime.now()

    date = t.date()
    date = str(date)

    try:
        basics = ts.get_stock_basics()
        basics.to_csv('d:/analyze_data/all.csv')
    except:
        basics = pd.read_csv('d:/analyze_data/all.csv')

    basics = basics[basics['outstanding'] < 5]
    print(len(basics))

    tp = ThreadPool()
    tp.map(get_bid, basics.index)

    print(datetime.datetime.now() - t)
