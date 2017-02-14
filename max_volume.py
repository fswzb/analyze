"""量能研究"""
import datetime
from multiprocessing.pool import ThreadPool

from utils import get_hist_data, get_stock_basics


def update(code):
    hist = get_hist_data(code, start='2016-02-13')
    if hist is None or len(hist) < 10:
        return

    mean = hist['volume'].mean()
    hist['rate'] = (hist['volume'] / mean).round(2)
    hist = hist[['open', 'high', 'low', 'close', 'p_change', 'turnover', 'rate']]
    hist = hist.sort_values('rate', ascending=False)

    if len(hist) > 0:
        print(code, mean)
        print(hist)


if __name__ == '__main__':
    t = datetime.datetime.now()

    basics = get_stock_basics()
    tp = ThreadPool()
    tp.map(update, basics.index)

    print(datetime.datetime.now() - t)
