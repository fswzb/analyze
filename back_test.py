import os
from io import StringIO

import pandas as pd
import tushare as ts

from bbi_strategy import get_bbi_match


def get_hist(code, date):
    filename = 'd:/analyze_data/k/{}.csv'.format(code)
    if os.path.exists(filename):
        text = open(filename, encoding='GBK').read()
        text = text.replace('--', '')
        df = pd.read_csv(StringIO(text), dtype={'date': 'object'})
        df = df.set_index('date')

        return df.loc[date]


def explore(date):
    # 止盈
    if len(position_list) > 0:
        position_list[0]['days'] += 1

        hist = get_hist(position_list[0]['code'], date)
        if hist is not None:
            position_list[0]['profit'] = (hist['open'] - position_list[0]['buy_price']) / position_list[0]['buy_price']

            if position_list[0]['days'] >= hold_days and position_list[0]['profit'] < hold:
                position_list.clear()
                print('sell')
            if position_list[0]['profit'] > 0:
                pass

    # 止损
    pass

    # 建仓
    if len(position_list) == 0 and len(buy_list) > 0:
        code = buy_list[0]
        filename = 'd:/analyze_data/k/{}.csv'.format(code)
        if os.path.exists(filename):
            text = open(filename, encoding='GBK').read()
            text = text.replace('--', '')
            df = pd.read_csv(StringIO(text), dtype={'date': 'object'})
            df = df.set_index('date')

            buy_list.clear()

            tick = {'code': code, 'date': date, 'buy_price': df.loc[date]['open'], 'days': 1,
                    'high': df.loc[date]['high'], 'profit': 0}
            position_list.append(tick)
            print(tick)

    # 选股
    if len(buy_list) == 0:
        code = get_bbi_match()
        if code is not None:
            buy_list.append(code)


hold_days = 17
zhi_sun = -.15
zhi_ying = -.04
hold = .05

buy_list = []
position_list = []
if __name__ == '__main__':
    sh = ts.get_hist_data('sh')
    sh = sh[sh.index >= '2016-02-01']
    sh = sh.iloc[::-1]
    # print(sh)

    for date, row in sh.iterrows():
        explore(date)
