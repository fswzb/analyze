"""二板"""
import datetime
import threading
from multiprocessing.pool import ThreadPool

import numpy as np
import pandas as pd

import tushare as ts
from easyutils import get_stock_type
from utils import get_k_data


def explore_second_rise(index):
    global start, end, p_change_array, mu, sh

    hist = ts.get_hist_data(index, start=start, end=end)

    if hist is None:
        return

    _len = len(hist)
    if _len < 4:  # 第一天用来计算第三天是否是二板，第四天计算收益
        return

    hist = hist.iloc[::-1]
    # print(hist)

    pChange = hist['p_change']
    ma5 = hist['ma5']
    ma10 = hist['ma10']
    ma20 = hist['ma20']

    for i in range(2, _len):
        # 二板策略
        if pChange[i - 3] > 9.5:  # 第一天涨停，则第三天不是二板
            continue
        if pChange[i - 2] <= 9.5 or pChange[i - 1] <= 9.5:  # 第二天第三天得是板
            continue
        if hist['high'][i - 1] == hist['low'][i - 1]:  # 第三天不能是一字板
            continue

        # TODO 检查是否放量

        # 板后低开策略
        if pChange[i - 2] <= 9.5:  # 板
            continue
        if hist['open'][i - 1] >= hist['close'][i - 2]:  # 低开
            continue

        # 大盘上行
        # mssh0 = sh.get_value(hist.index[i - 3], 'ma5')
        # mssh1 = sh.get_value(hist.index[i - 2], 'ma5')
        # if mssh0 >= mssh1:  # 大盘上行
        #     continue

        # 个股上行
        # if ma5[i - 1] > ma10[i - 1] > ma20[i - 1]:
        #     if ma5[i - 0] > ma10[i - 0] > ma20[i - 0]:
        #         if ma5[i - 1] > ma5[i - 0] and ma10[i - 1] > ma10[i - 0] and ma20[i - 1] > ma20[i - 0]:

        # if ma10[i - 3] >= ma10[i - 2]:  # 个股上行
        #     continue

        benefit = round((hist['open'][i] - hist['open'][i - 1]) / hist['open'][i - 1] * 100, 2)  # 低开买入，开盘即抛
        benefit = round((hist['close'][i] - hist['open'][i - 1]) / hist['open'][i - 1] * 100, 2)  # 低开买入，收盘抛出

        mu.acquire()
        # p_change_array.append(pChange[i])
        p_change_array.append(benefit)
        code_date[index] = hist.index[i]
        mu.release()

        if benefit < -5:
            # if benefit > 5:
            print('https://xueqiu.com/S/{}{}'.format(get_stock_type(index), index), hist.index[i], benefit)


def get_high_time(index):
    if index not in code_date:
        return

    df = get_k_data(index, code_date[index], '5')
    if df is None:
        return

    max = df['high'].max()

    mu.acquire()
    dt = df[df['high'] == max]
    for i, row in dt.iterrows():
        key = str(i)
        key = key[len(key) - 8:]
        if key in time_dict:
            time_dict[key] += 1
        else:
            time_dict[key] = 1
    mu.release()


def draw_chart(df):
    import seaborn as sns
    sns.set(style="white")
    sns.pointplot(df.index, df['count'])
    sns.plt.show()


def calc_distribute(basics):
    pool = ThreadPool()
    pool.map(get_high_time, basics.index)

    # print('t_dict', time_dict)
    df = pd.DataFrame({'time': list(time_dict.keys()), 'count': list(time_dict.values())})
    df = df.sort_values('count')
    df = df.reset_index(drop=True)
    # print(df)

    df = df.sort_values('time')
    df = df.reset_index(drop=True)
    # print(df)

    draw_chart(df)


start = None
end = None

p_change_array = []
code_date = {}
time_dict = {}
mu = threading.Lock()

sh = None

if __name__ == '__main__':
    s = datetime.datetime.now()

    global start, end, p_change_array, sh

    t = datetime.datetime.now() - datetime.timedelta(days=365 * 1 / 1)
    day = t.date()
    start = str(day)

    t = datetime.datetime.now() - datetime.timedelta(days=0 + 0)
    day = t.date()
    end = str(day)

    sh = ts.get_hist_data('sh')

    # 计算二板收益
    basics = ts.get_stock_basics()
    pool = ThreadPool()
    pool.map(explore_second_rise, basics.index)

    print(p_change_array)
    print('机会', len(p_change_array))

    n = np.array(p_change_array)
    positive = (n > 0).sum()
    print('有收益', positive)
    print('无收益', len(n) - positive)
    print('获利概率', '{}%'.format(round(positive / len(n) * 100, 2)))
    print('平均收益', '{}%'.format(round(n.mean(), 2)))

    # 计算高价位分布
    # calc_distribute(basics)

    print('end')

    print(datetime.datetime.now() - s)
