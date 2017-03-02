"""BBI大于5小于10；量比大于0.5小于3；换手率大于2%小于7%；按总市值从小到大排列"""
import json
import os
import threading
from io import StringIO

import pandas as pd

from utils import get_stock_basics


def get_bbi_match(date):
    ignore_list = json.load(open('ignore_list.json', encoding='utf8'))
    ignore_list = []

    poll = pd.DataFrame(columns=['code', 'bbi', '量比', 'turnover', 'totalAssets'])
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
                poll = poll.append({'code': index, 'bbi': row['bbi'], '量比': row['量比'], 'turnover': row['turnover'],
                                    'totalAssets': row['totals'] * hist['close'][0]}, ignore_index=True)

    # print(poll)

    poll = poll[poll['turnover'].between(2, 7)]
    poll = poll[poll['量比'].between(0.5, 3)]
    poll = poll[poll['bbi'].between(5, 10)]
    poll = poll.sort_values('totalAssets')

    # print(poll)
    if len(poll) > 0:
        return poll.iloc[0]['code']


if __name__ == '__main__':
    print(get_bbi_match('2016-03-17'))
