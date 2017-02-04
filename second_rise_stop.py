'''二板'''
import datetime
import threading
from multiprocessing.pool import ThreadPool

import numpy as np
import pandas as pd

import tushare as ts
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
        if pChange[i - 3] > 9.5:  # 第一天涨停，则第三天不是二板
            continue
        if pChange[i - 2] <= 9.5 or pChange[i - 1] <= 9.5:  # 第二天第三天得是板
            continue
        if hist['high'][i - 1] == hist['low'][i - 1]:  # 第三天不能是一字板
            continue

        # TODO 检查是否放量

        # mssh0 = sh.get_value(hist.index[i - 3], 'ma5')
        # mssh1 = sh.get_value(hist.index[i - 2], 'ma5')
        # if mssh0 >= mssh1:  # 大盘上行
        #     continue

        # if ma5[i - 1] > ma10[i - 1] > ma20[i - 1]:
        #     if ma5[i - 0] > ma10[i - 0] > ma20[i - 0]:
        #         if ma5[i - 1] > ma5[i - 0] and ma10[i - 1] > ma10[i - 0] and ma20[i - 1] > ma20[i - 0]:

        # if ma10[i - 3] >= ma10[i - 2]:  # 个股上行
        #     continue

        mu.acquire()
        p_change_array.append(pChange[i])
        code_date[index] = hist.index[i]
        mu.release()


def get_high_time(index):
    if index not in code_date:
        return

    df = get_k_data(index, code_date[index], '5')
    if df is None:
        return

    max = df['high'].max()

    mu.acquire()
    dt = df[df['high'] == max].index
    for i in dt:
        key = str(i)
        key = key[len(key) - 8:]
        if key in t_dict:
            t_dict[key] += 1
        else:
            t_dict[key] = 1
    mu.release()


start = None
end = None

p_change_array = []
code_date = {}
t_dict = {}
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

    basics = ts.get_stock_basics()
    pool = ThreadPool()
    pool.map(explore_second_rise, basics.index)

    print(p_change_array)
    print('len', len(p_change_array))

    n = np.array(p_change_array)
    print((n > 0).sum())
    print((n <= 0).sum())
    print(n.mean())

    pool = ThreadPool()
    pool.map(get_high_time, basics.index)

    print('t_dict', t_dict)
    df = pd.DataFrame({'time': list(t_dict.keys()), 'count': list(t_dict.values())})
    df = df.sort_values('count')
    print(df)

    '''   count      time
    4      1  15:00:00
    9     16  14:30:00
    7     23  13:30:00
    3     24  11:00:00
    2     27  10:30:00
    6     27  13:00:00
    5     32  14:00:00
    0     52  10:00:00
    1     78  09:00:00
    8    224  09:30:00'''

    '''    count      time
    0      57  10:05:00
    33     57  09:45:00
    21     58  10:00:00
    35     60  10:10:00
    2      61  09:55:00
    32     61  11:30:00
    31     63  09:40:00
    12     64  10:15:00
    43     66  09:50:00
    44     68  13:05:00
    41     68  10:20:00
    27     68  13:15:00
    15     68  10:35:00
    38     69  10:50:00
    17     70  10:45:00
    18     71  10:30:00
    47     71  10:25:00
    28     72  13:10:00
    50     72  11:25:00
    37     74  13:00:00
    39     74  09:35:00
    9      74  10:40:00
    5      74  13:40:00
    29     74  11:20:00
    14     75  10:55:00
    22     75  13:35:00
    1      75  11:15:00
    34     76  13:20:00
    24     76  11:10:00
    16     76  13:30:00
    45     77  11:05:00
    23     78  09:25:00
    30     79  13:50:00
    20     79  13:45:00
    3      80  14:05:00
    46     80  13:55:00
    25     81  13:25:00
    8      81  14:00:00
    26     81  11:00:00
    4      83  14:10:00
    10     88  14:20:00
    7      91  14:25:00
    42     91  14:15:00
    6      92  14:35:00
    11     92  14:30:00
    40     93  15:00:00
    36     94  14:40:00
    49     95  14:50:00
    19     95  14:45:00
    13     96  14:55:00
    48    156  09:30:00'''

    df = df.sort_values('time')
    print(df)

    '''    count      time
    30     78  09:25:00
    7     124  09:30:00
    2      34  09:35:00
    24     22  09:40:00
    31     12  09:45:00
    3      19  09:50:00
    19     13  09:55:00
    11     11  10:00:00
    4       7  10:05:00
    18     10  10:10:00
    41     10  10:15:00
    44      5  10:20:00
    5       9  10:25:00
    25      9  10:30:00
    17      4  10:35:00
    38      7  10:40:00
    27      1  10:45:00
    0       2  10:50:00
    8       4  10:55:00
    1       6  11:00:00
    45      6  11:05:00
    32      3  11:10:00
    22      4  11:15:00
    46      3  11:20:00
    37      2  11:25:00
    43      4  13:00:00
    35      3  13:05:00
    29      4  13:10:00
    9       1  13:15:00
    23      6  13:20:00
    34      9  13:25:00
    26      2  13:30:00
    39      1  13:35:00
    10      3  13:40:00
    21      5  13:45:00
    40      5  13:50:00
    33      7  13:55:00
    48      6  14:00:00
    6       6  14:05:00
    47      6  14:10:00
    15      8  14:15:00
    28      4  14:20:00
    12      2  14:25:00
    20      6  14:30:00
    36      2  14:35:00
    16      4  14:40:00
    13      1  14:50:00
    42      3  14:55:00
    14      1  15:00:00'''

    '''    count      time
    23     78  09:25:00
    48    156  09:30:00
    39     74  09:35:00
    31     63  09:40:00
    33     57  09:45:00
    43     66  09:50:00
    2      61  09:55:00
    21     58  10:00:00
    0      57  10:05:00
    35     60  10:10:00
    12     64  10:15:00
    41     68  10:20:00
    47     71  10:25:00
    18     71  10:30:00
    15     68  10:35:00
    9      74  10:40:00
    17     70  10:45:00
    38     69  10:50:00
    14     75  10:55:00
    26     81  11:00:00
    45     77  11:05:00
    24     76  11:10:00
    1      75  11:15:00
    29     74  11:20:00
    50     72  11:25:00
    32     61  11:30:00
    37     74  13:00:00
    44     68  13:05:00
    28     72  13:10:00
    27     68  13:15:00
    34     76  13:20:00
    25     81  13:25:00
    16     76  13:30:00
    22     75  13:35:00
    5      74  13:40:00
    20     79  13:45:00
    30     79  13:50:00
    46     80  13:55:00
    8      81  14:00:00
    3      80  14:05:00
    4      83  14:10:00
    42     91  14:15:00
    10     88  14:20:00
    7      91  14:25:00
    11     92  14:30:00
    6      92  14:35:00
    36     94  14:40:00
    19     95  14:45:00
    49     95  14:50:00
    13     96  14:55:00
    40     93  15:00:00'''

    print('end')

    print(datetime.datetime.now() - s)
