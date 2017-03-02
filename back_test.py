import os
from io import StringIO

import pandas as pd
import tushare as ts

from bbi_strategy import get_bbi_match_2
from utils import get_k_data


def get_hist(code, date):
    filename = 'd:/analyze_data/k/{}.csv'.format(code)
    if os.path.exists(filename):
        text = open(filename, encoding='GBK').read()
        text = text.replace('--', '')
        df = pd.read_csv(StringIO(text), dtype={'date': 'object'})
        df = df.set_index('date')

        if date in list(df.index):
            return df.loc[date]


def explore(date):
    global rate, count
    sold = False
    if len(position_list) > 0:
        position_list[0]['days'] += 1

        code = position_list[0]['code']
        hist = get_hist(code, date)
        if hist is not None:
            mk = get_k_data(code, date=date, ktype='1')
            if mk is None:
                print(code, date)
                return

            position_list[0]['profit'] = (hist['open'] - position_list[0]['buy_price']) / position_list[0][
                'buy_price'] / 1.001
            position_list[0]['profit'] = round(position_list[0]['profit'], 3)

            # 时间到换仓
            if len(position_list) > 0:
                if position_list[0]['days'] >= HOLD_DAYS and position_list[0]['profit'] < HOLD:
                    position_list[0]['sell_date'] = date
                    position_list[0]['sell_price'] = hist['open']
                    print(position_list[0])
                    rate *= 1 + position_list[0]['profit']
                    print(rate)
                    position_list.clear()
                    sold = True

            # 最大回撤、止盈
            if len(position_list) > 0:
                if position_list[0]['high'] > 0:
                    for i, row in mk.iterrows():
                        if (row['close'] - position_list[0]['high']) / position_list[0]['high'] / 1.001 < ZHI_YING:
                            position_list[0]['profit'] = (row['close'] - position_list[0]['buy_price']) / \
                                                         position_list[0]['buy_price']
                            position_list[0]['sell_date'] = date
                            position_list[0]['sell_price'] = row['close']
                            print(position_list[0])
                            rate *= 1 + position_list[0]['profit']
                            print(rate)
                            position_list.clear()
                            sold = True
                            break

            # 止损
            if len(position_list) > 0:
                for i, row in mk.iterrows():
                    if (row['close'] - position_list[0]['buy_price']) / position_list[0]['buy_price'] / 1.001 < ZHI_SUN:
                        position_list[0]['profit'] = (row['close'] - position_list[0]['buy_price']) / position_list[0][
                            'buy_price'] / 1.001
                        position_list[0]['sell_date'] = date
                        position_list[0]['sell_price'] = row['close']
                        print(position_list[0])
                        rate *= 1 + position_list[0]['profit']
                        print(rate)
                        position_list.clear()
                        sold = True
                        break

            # 收盘，更新最高价
            if len(position_list) > 0:
                position_list[0]['profit'] = (hist['close'] - position_list[0]['buy_price']) / position_list[0][
                    'buy_price'] / 1.001
                position_list[0]['profit'] = round(position_list[0]['profit'], 3)
                if position_list[0]['profit'] > 0:
                    position_list[0]['high'] = max(position_list[0]['high'], hist['high'])

    # 建仓
    if len(position_list) == 0 and len(buy_list) > 0 and sold == False:
        code = buy_list[0]
        filename = 'd:/analyze_data/k/{}.csv'.format(code)
        if os.path.exists(filename):
            text = open(filename, encoding='GBK').read()
            text = text.replace('--', '')
            df = pd.read_csv(StringIO(text), dtype={'date': 'object'})
            df = df.set_index('date')

            buy_list.clear()

            if date in list(df.index):
                tick = {'code': code, 'buy_date': date, 'buy_price': df.loc[date]['open'], 'days': 1,
                        'high': 0, 'profit': 0}
                position_list.append(tick)
                position_list[0]['profit'] = (df.loc[date]['close'] - position_list[0]['buy_price']) / position_list[0][
                    'buy_price'] / 1.001
                position_list[0]['profit'] = round(position_list[0]['profit'], 3)
                if position_list[0]['profit'] > 0:
                    position_list[0]['high'] = max(position_list[0]['high'], df.loc[date]['high'])
                print(tick)

                count += 1

    # 选股
    if len(position_list) == 0:
        code = get_bbi_match_2(date)
        if code is not None:
            buy_list.clear()
            buy_list.append(code)


HOLD_DAYS = 17
ZHI_SUN = -.15
ZHI_YING = -.04
HOLD = .05

rate = 1
count = 0
opd = False

buy_list = []
position_list = []
if __name__ == '__main__':
    # sh = ts.get_hist_data('sh')
    # sh = sh[sh.index >= '2000-01-01']
    # sh = sh.iloc[::-1]
    # print(sh)

    sh = ts.trade_cal()
    sh['calendarDate'] = pd.to_datetime(sh['calendarDate'])
    sh = sh.set_index('calendarDate')

    for date, row in sh.iterrows():
        date = str(date)[:10]
        if row['isOpen'] == 1:
            explore(date)

    print(count)
    print(rate - 1)
