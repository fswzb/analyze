"""首日涨停，次日跌停，第三日突破分时均线"""
import datetime
import threading
from multiprocessing.pool import ThreadPool

import numpy as np

import tushare as ts
from easyutils import get_stock_type


def explore_growth_form(code):
    # hist = ts.get_h_data(code)
    hist = ts.get_hist_data(code, start=start, end=end)
    if hist is None:
        return

    hist_len = len(hist)
    if hist_len == 0:
        return

    hist = hist.iloc[::-1]

    # pre_close = list(hist['close'])
    # pre_close.pop()
    # pre_close.insert(0, hist['high'][0] / 1.1)
    #
    # hist['pre_close'] = pre_close
    #
    # hist['rise_stop'] = np.round(hist['pre_close'] * 1.1, 2)
    # hist['fall_stop'] = np.round(hist['pre_close'] / 1.1, 2)

    # print(hist)

    average_volume = hist['volume'].mean()

    from_index = -1
    for i in range(1, hist_len):
        if i < from_index:
            continue
        if i + 4 >= hist_len:
            continue

        # if hist['p_change'][i] > 9:  # 涨停
        #     if hist['p_change'][i + 1] < -8:  # 跌停
        #         if hist['volume'][i + 1] < hist['volume'][i]:  # 缩量
        #             if (hist['open'][i + 2] - hist['close'][i + 1]) / hist['close'][i + 1] > -.05:  # 不跌破5个点

        # if hist['p_change'][i] > 5:  # 上涨5%
        #     if hist['p_change'][i + 1] > 5:  # 上涨5%
        #         if hist['p_change'][i + 2] > 5:  # 上涨5%
        #             if hist['high'][i + 3] != hist['low'][i + 3]:  # 能买得进

        # if hist['p_change'][i] > 4:  # 上涨4%
        #     if hist['p_change'][i + 1] > 4:  # 上涨4%
        #         if hist['high'][i + 2] != hist['low'][i + 2]:  # 能买得进
        #
        #             if hist['close'][i + 2] < hist['close'][i + 1]:  # 买入当天收盘比前一天底，第二天开盘卖出
        #                 j = i + 3
        #                 benefit = (hist['open'][j] - hist['open'][i + 2]) / hist['open'][i + 2]
        #             else:
        #                 for j in range(i + 3, hist_len):
        #                     if hist['close'][j] < hist['close'][j - 1]:  # 收盘比前一天的底，收盘卖出
        #                         break
        #                 benefit = (hist['close'][j] - hist['open'][i + 2]) / hist['open'][i + 2]

        # if hist['p_change'][i] < 3:  # 上涨4%
        #     if hist['p_change'][i + 1] < 3:  # 上涨4%
        #         if hist['ma5'][i + 1] > hist['ma5'][i]:
        #             if hist['high'][i + 2] != hist['low'][i + 2] and hist['high'][i + 2] > 9.5:  # 能买得进

        if i + 10 < hist_len:
            sum_volume = 0
            for k in range(8):
                sum_volume += hist['volume'][i + k]

            if sum_volume / 8 < average_volume:
                # if (hist['close'][i + 8] - hist['close'][i]) / hist['close'][i] < 0.1:  # 两周内上涨不超过10%
                if hist['high'][i + 9] != hist['low'][i + 9] and hist['high'][i + 9] > 9.5:  # 能买得进

                    benefit = (hist['close'][i + 10] - hist['high'][i + 9]) / hist['high'][i + 9]
                    benefit = round(benefit * 100, 2)

                    mu.acquire()
                    benefits.append(benefit)
                    mu.release()

                    print('https://xueqiu.com/S/{}{}'.format(get_stock_type(code), code), hist.index[i + 9],
                          # hist.index[j], j - (i + 2),
                          benefit)

                    # from_index = j


mu = threading.Lock()
benefits = []
start = None
end = None
if __name__ == '__main__':
    s = datetime.datetime.now()

    t = datetime.datetime.now() - datetime.timedelta(days=365 * 1 / 1)
    day = t.date()
    start = str(day)

    t = datetime.datetime.now() - datetime.timedelta(days=0 + 0)
    day = t.date()
    end = str(day)

    basics = ts.get_stock_basics()
    tp = ThreadPool()
    tp.map(explore_growth_form, basics.index)

    # print(benefits)
    print('机会', len(benefits))

    n = np.array(benefits)
    positive = (n > 0).sum()
    print('有收益', positive)
    print('无收益', len(n) - positive)
    print('获利概率', '{}%'.format(round(positive / len(n) * 100, 2)))
    print('平均收益', '{}%'.format(round(n.mean(), 2)))

    print(datetime.datetime.now() - s)
