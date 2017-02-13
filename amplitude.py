"""振幅研究，
统计下来并无法计算巨大振幅出现时机"""
import datetime
from multiprocessing.pool import ThreadPool

from utils import get_hist_data, get_stock_basics, get_settlement


def update(code):
    hist = get_hist_data(code, start='2016-02-13')
    if hist is None or len(hist) < 10:
        return

    settlement = get_settlement(hist)
    amplitude = ((hist['high'] - hist['low']) / settlement * 100).round(2)
    hist['amplitude'] = amplitude
    hist = hist[amplitude > 12]
    hist = hist[hist['p_change'] > 0]
    hist = hist[['open', 'high', 'low', 'close', 'p_change', 'turnover', 'amplitude']]

    if len(hist) > 0:
        print(code)
        print(hist['p_change'].mean())
        print(hist)


if __name__ == '__main__':
    t = datetime.datetime.now()

    basics = get_stock_basics()
    tp = ThreadPool()
    tp.map(update, basics.index)

    print(datetime.datetime.now() - t)
