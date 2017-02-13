"""高开策略，研究高开规律"""
import datetime
from multiprocessing.pool import ThreadPool

from utils import get_stock_basics, get_hist_data, get_settlement


def explore_open(code):
    hist = get_hist_data(code, start='2016-02-13')
    if hist is None or len(hist) < 10:
        return

    hist['settlement'] = get_settlement(hist)
    hist['openpercent'] = ((hist['open'] - hist['settlement']) / hist['settlement'] * 100).round(2)
    hist = hist[hist['openpercent'] > 2]
    hist = hist[['open', 'high', 'low', 'close', 'openpercent', 'p_change', 'turnover']]

    if len(hist) > 0:
        print('+++++++++++++++++++++++++++++')
        print(code)
        print(hist['p_change'].mean())
        print(hist)


if __name__ == '__main__':
    t = datetime.datetime.now()

    basics = get_stock_basics()
    tp = ThreadPool()
    tp.map(explore_open, basics.index)

    print(datetime.datetime.now() - t)
