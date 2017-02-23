import datetime
import os
import threading
from multiprocessing.pool import ThreadPool

import pandas as pd
from pandas.compat import StringIO

import tushare as ts


def explore(iter):
    global month_growth, quarter_growth, half_year_growth, year_growth

    code = iter[0]
    row = iter[1]

    filename = 'd:/analyze_data/k/{}.csv'.format(code)
    if not os.path.exists(filename):
        return

    text = open(filename, encoding='GBK').read()
    text = text.replace('--', '')
    df = pd.read_csv(StringIO(text), dtype={'date': 'object'})
    df = df.set_index('date')

    df = df.head(len(df) - 20)

    for i in range(0, min(20 * 12 + 1, len(df)), 20):
        if i not in i_arr:
            continue

        close_i = df['close'][i]
        growth = (df['close'][0] - close_i) / close_i * 100
        growth = round(growth, 2)
        d = {'code': code, 'outstanding': row['outstanding'], 'liquid_assets': row['outstanding'] * close_i,
             'totals': row['totals'], 'totalAssets': row['totalAssets'] * close_i, 'growth': growth}

        mu.acquire()
        if i == 20 * 1:
            month_growth = month_growth.append(d, ignore_index=True)
        elif i == 20 * 3:
            quarter_growth = quarter_growth.append(d, ignore_index=True)
        elif i == 20 * 6:
            half_year_growth = half_year_growth.append(d, ignore_index=True)
        elif i == 20 * 12:
            year_growth = year_growth.append(d, ignore_index=True)
        mu.release()


i_arr = [20 * 1, 20 * 3, 20 * 6, 20 * 12]
columns = ['code', 'outstanding', 'liquid_assets', 'totals', 'totalAssets', 'growth']
month_growth = pd.DataFrame(columns=columns)
quarter_growth = pd.DataFrame(columns=columns)
half_year_growth = pd.DataFrame(columns=columns)
year_growth = pd.DataFrame(columns=columns)
mu = threading.Lock()
if __name__ == '__main__':
    now = datetime.datetime.now()
    today = str(now.date())

    lst = os.listdir('d:/analyze_data/k/')
    basics = ts.get_stock_basics()
    tp = ThreadPool()
    tp.map(explore, basics.iterrows())

    month_growth.to_csv('data/{}_month_{}.csv'.format(os.path.basename(__file__), today))
    quarter_growth.to_csv('data/{}_quarter_{}.csv'.format(os.path.basename(__file__), today))
    half_year_growth.to_csv('data/{}_half_year_{}.csv'.format(os.path.basename(__file__), today))
    year_growth.to_csv('data/{}_year_{}.csv'.format(os.path.basename(__file__), today))

    month_g = month_growth.sort_values('liquid_assets').head(10)['growth'].mean()
    print(round(month_g, 2))
    quarter_g = quarter_growth.sort_values('liquid_assets').head(10)['growth'].mean()
    print(round(quarter_g, 2))
    half_year_g = half_year_growth.sort_values('liquid_assets').head(10)['growth'].mean()
    print(round(half_year_g, 2))
    year_g = year_growth.sort_values('liquid_assets').head(10)['growth'].mean()
    print(round(year_g, 2))

    print(datetime.datetime.now() - now)
