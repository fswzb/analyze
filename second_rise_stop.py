import datetime
import tushare as ts
from multiprocessing.pool import ThreadPool

def explore_second_rise(index):
    hist = ts.get_k_data(index, start='20150116', end='20161216')
    hist = hist.tail(len(hist) - 30)
    if len(hist) == 0:
        return
    print(len(hist))

if __name__ == '__main__':
    s=datetime.datetime.now()

    basics = ts.get_stock_basics()
    pool = ThreadPool()
    pool.map(explore_second_rise, basics.index)

    print('end')

    print(datetime.datetime.now()-s)