import datetime
import os
import threading
import time
from multiprocessing.pool import ThreadPool

import pandas as pd
import tushare as ts
from pandas.compat import StringIO


def explore(row_iter):
    global rise_stop_df

    code = row_iter[0]
    row = row_iter[1]

    print(code)

    filename = 'd:/analyze_data/k/{}.csv'.format(code)
    if not os.path.exists(filename):
        return

    text = open(filename, encoding='GBK').read()
    text = text.replace('--', '')
    df = pd.read_csv(StringIO(text), dtype={'date': 'object'})
    df = df.set_index('date')

    # df = ts.get_hist_data(code)
    # if df is None or len(df) == 0:
    #     return

    # df = df.head(len(df) - 20)
    # df = df.dropna()
    df = df.iloc[::-1]

    for i in range(len(df)):
        if df['p_change'][i] < 9:
            break

    df = df.tail(len(df) - i)

    for i in range(len(df)):
        try:
            if df['p_change'][i] > 9:
                open_i = df['open'][i]

                t = time.strptime(df.index[i], '%Y-%m-%d')
                y, m, d = t[0:3]
                ymd = datetime.datetime(y, m, d)
                # print(ymd.weekday())

                d = {'code': code, 'outstanding': row['outstanding'], 'liquid_assets': row['outstanding'] * open_i,
                     'totals': row['totals'], 'totalAssets': row['totalAssets'] * open_i, 'growth': 0,
                     'weekday': ymd.weekday(), 'month': m, 'day': d}

                mu.acquire()
                rise_stop_df = rise_stop_df.append(d, ignore_index=True)
                mu.release()
        except Exception as e:
            print(e)
            print(i)
            print(code)
            print(df)


columns = ['code', 'outstanding', 'liquid_assets', 'totals', 'totalAssets', 'growth', 'weekday', 'month', 'day']
rise_stop_df = pd.DataFrame(columns=columns)
mu = threading.Lock()
if __name__ == '__main__':
    now = datetime.datetime.now()
    today = str(now.date())

    lst = os.listdir('d:/analyze_data/k/')
    basics = ts.get_stock_basics()
    tp = ThreadPool()
    tp.map(explore, basics.iterrows())

    rise_stop_df.to_csv('data/{}_{}.csv'.format(os.path.basename(__file__), today))

    print(datetime.datetime.now() - now)
