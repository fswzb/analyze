"""BBI大于5小于10；量比大于0.5小于3；换手率大于2%小于7%；按总市值从小到大排列"""
import json
import os
from io import StringIO

import pandas as pd

import tushare as ts
from utils import get_stock_basics


def get_bbi_match(date):
    ignore_list = json.load(open('ignore_list.json', encoding='utf8'))
    ignore_list = []

    # basics = get_stock_basics()
    basics = get_stock_basics()
    hist = ts.get_hist_data('sh')
    poll = pd.DataFrame(columns=['code', 'bbi', '量比', 'turnover', 'totalAssets'])
    date = hist.index[0]
    for index, row in basics.iterrows():
        if index in ignore_list:
            # print(index)
            continue

        filename = 'd:/analyze_data/k/{}.csv'.format(index)
        if os.path.exists(filename):
            text = open(filename, encoding='GBK').read()
            text = text.replace('--', '')
            df = pd.read_csv(StringIO(text), dtype={'date': 'object'})
            df = df.set_index('date')

            if df.index[0] == date:
                row['bbi'] = (df['close'].head(3).mean() + df['close'].head(6).mean() + df['close'].head(12).mean() +
                              df['close'].head(24).mean()) / 4
                row['量比'] = df['volume'][0] / (df['volume'].head(6).tail(5).mean())
                row['turnover'] = df['turnover'][0]
                poll = poll.append({'code': index, 'bbi': row['bbi'], '量比': row['量比'], 'turnover': row['turnover'],
                                    'totalAssets': row['totals'] * df['close'][0]}, ignore_index=True)

    # print(poll)

    poll = poll[poll['turnover'].between(2, 7)]
    poll = poll[poll['量比'].between(0.5, 3)]
    poll = poll[poll['bbi'].between(5, 10)]
    poll = poll.sort_values('totalAssets')

    # print(poll)
    if len(poll) > 0:
        return poll.iloc[0]['code']


if __name__ == '__main__':
    print(get_bbi_match('2017-03-02'))
