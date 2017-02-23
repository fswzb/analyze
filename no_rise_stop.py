import datetime
import os
import threading
from multiprocessing.pool import ThreadPool

import pandas as pd

import tushare as ts
from easyutils import get_stock_type


def explore(index):
    hist = ts.get_hist_data(index, start='2016-02-23')
    if hist is None or len(hist) == 0:
        return

    hist = hist.head(len(hist) - 20)  # 去掉上市初期的一字板
    if len(hist) < 20:
        return

    hist = hist.iloc[::-1]
    count = 0
    start = None
    for i in range(len(hist)):
        if hist['p_change'][i] > 0:
            count += 1
            if start is None:
                start = hist.index[i]
        else:
            if count > 5:
                d = {'code': index, 'start': start, 'count': count,
                     'url': 'https://xueqiu.com/S/{}{}'.format(get_stock_type(index).upper(), index)}
                mu.acquire()
                global df
                df = df.append(d, ignore_index=True)
                mu.release()
                print(d)
            count = 0
            start = None


df = pd.DataFrame(columns=['code', 'start', 'count', 'url'])
mu = threading.Lock()
if __name__ == '__main__':
    now = datetime.datetime.now()

    basics = ts.get_stock_basics()
    tp = ThreadPool()
    tp.map(explore, basics.index)

    df = df.sort_values('code')
    df = df.reset_index(drop=True)
    df.to_csv('data/{}_{}.csv'.format(os.path.basename(__file__), str(now.date())))

    print(datetime.datetime.now() - now)
