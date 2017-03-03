import datetime
import os
import threading
from io import StringIO
from multiprocessing.pool import ThreadPool

import pandas as pd

from utils import get_stock_basics


def update_day():
    def f(iterrow):
        try:
            code = iterrow[0]
            info = iterrow[1]

            print(code)

            filename = 'd:/analyze_data/k/{}.csv'.format(code)
            if os.path.exists(filename):
                text = open(filename, encoding='GBK').read()
                text = text.replace('--', '')
                hist = pd.read_csv(StringIO(text), dtype={'date': 'object'})
                hist = hist.set_index('date')

                hist_close = hist['close']
                for i in range(len(hist)):
                    k = hist.iloc[i]
                    date = k.name

                    d = {'code': code, 'date': date, 'outstanding': info['outstanding'], 'totals': info['totals'],
                         'totalAssets': info['totals'] * k['close']}
                    d['bbi'] = (hist_close.iloc[i:i + 3].mean() + hist_close.iloc[i:i + 6].mean()
                                + hist_close.iloc[i:i + 12].mean() + hist_close.iloc[i:i + 24].mean()) / 4
                    d['量比'] = k['volume'] / (hist['volume'].iloc[i:i + 6].tail(5).mean())
                    d['turnover'] = k['turnover']

                    mu.acquire()
                    df = all_days[date] if date in all_days else pd.DataFrame(columns=columns)
                    df = df.append(d, ignore_index=True)
                    all_days[date] = df
                    mu.release()
        except Exception as e:
            print(e)
            print(iterrow)

    all_days = {}
    columns = ['code', 'date', 'outstanding', 'totals', 'totalAssets', 'bbi', '量比', 'turnover']

    basics = get_stock_basics()
    # basics = basics.head(50)

    mu = threading.Lock()
    tp = ThreadPool()
    tp.map(f, basics.iterrows())

    # for iterrow in basics.iterrows():
    #     f(iterrow)

    path = 'd:/analyze_data/day'
    if not os.path.exists(path):
        os.makedirs(path)

    for (k, v) in all_days.items():
        v = v.set_index('code')
        v.to_csv('{}/{}.csv'.format(path, k))


if __name__ == '__main__':
    t = datetime.datetime.now()
    update_day()
    print(datetime.datetime.now() - t)
