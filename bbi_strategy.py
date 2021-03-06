"""BBI大于5小于10；量比大于0.5小于3；换手率大于2%小于7%；按总市值从小到大排列"""
import datetime
import json
import os
import threading
from io import StringIO

import pandas as pd

from utils import get_stock_basics


def get_bbi_match_2(date):
    filename = 'd:/analyze_data/day/{}.csv'.format(date)
    if os.path.exists(filename):
        text = open(filename, encoding='GBK').read()
        text = text.replace('--', '')
        pool = pd.read_csv(StringIO(text), dtype={'code': 'object'})
        pool = pool.set_index('code')

        pool = pool[pool['turnover'].between(2, 7)]
        pool = pool[pool['量比'].between(0.5, 3)]
        pool = pool[pool['bbi'].between(5, 10)]
        pool = pool.sort_values('totalAssets')

        # print(pool)
        if len(pool) > 0:
            return pool.iloc[0].name


def get_bbi_match(date):
    ignore_list = json.load(open('ignore_list.json', encoding='utf8'))
    ignore_list = []

    pool = pd.DataFrame(columns=['code', 'bbi', '量比', 'turnover', 'totalAssets'])
    mu = threading.Lock()

    # basics = get_stock_basics()
    basics = get_stock_basics()
    for index, row in basics.iterrows():
        if index in ignore_list:
            # print(index)
            continue

        filename = 'd:/analyze_data/k/{}.csv'.format(index)
        if os.path.exists(filename):
            text = open(filename, encoding='GBK').read()
            text = text.replace('--', '')
            hist = pd.read_csv(StringIO(text), dtype={'date': 'object'})
            hist = hist.set_index('date')

            hist = hist[hist.index <= date]

            if len(hist) == 0:
                continue

            if hist.index[0] == date:
                row['bbi'] = (hist['close'].head(3).mean() + hist['close'].head(6).mean() + hist['close'].head(
                    12).mean() +
                              hist['close'].head(24).mean()) / 4
                row['量比'] = hist['volume'][0] / (hist['volume'].head(6).tail(5).mean())
                row['turnover'] = hist['turnover'][0]
                pool = pool.append({'code': index, 'bbi': row['bbi'], '量比': row['量比'], 'turnover': row['turnover'],
                                    'totalAssets': row['totals'] * hist['close'][0]}, ignore_index=True)

    # print(pool)

    pool = pool[pool['turnover'].between(2, 7)]
    pool = pool[pool['量比'].between(0.5, 3)]
    pool = pool[pool['bbi'].between(5, 10)]
    pool = pool.sort_values('totalAssets')

    # print(pool)
    if len(pool) > 0:
        return pool.iloc[0]['code']


if __name__ == '__main__':
    t = datetime.datetime.now()
    today = str(t.date())

    print(get_bbi_match_2('2016-01-04'))

    print(get_bbi_match_2(today), datetime.datetime.now() - t)

    t = datetime.datetime.now()
    # print(get_bbi_match('2017-03-17'))
    print(get_bbi_match(today), datetime.datetime.now() - t)
