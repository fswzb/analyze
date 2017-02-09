"""大单扫货到，使股价达到涨停"""
import datetime
from multiprocessing.pool import ThreadPool

import pandas as pd
import tushare as ts
from pandas.compat import StringIO


def get_bid(index):
    hist = ts.get_sina_dd(index, date=date, vol=500)
    if hist is not None:
        print(index, hist['volume'].sum())


date = None
if __name__ == '__main__':
    t = datetime.datetime.now()

    date = t.date()
    date = str(date)

    text = open('d:/analyze_data/all.csv', encoding='GBK').read()
    text = text.replace('--', '')
    df = pd.read_csv(StringIO(text), dtype={'code': 'object'})
    basics = df.set_index('code')

    basics = basics[basics['outstanding'] < 5]
    print(len(basics))

    tp = ThreadPool()
    tp.map(get_bid, basics.index)

    print(datetime.datetime.now() - t)
