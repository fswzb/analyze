import tushare as ts

print('hello world')

df = ts.get_hist_data('002337').head(200)
df['limit_up'] = False
df['limit_up_r'] = df['close'] * 1.1
print(df)
print(df['p_change'].describe())

from pylab import *


def showTimeLine(df):
    # 按时间顺序展示涨幅
    n = len(df.index)
    X = np.arange(n)
    Y1 = df['p_change'].values

    bar(X, +Y1, facecolor='#9999ff', edgecolor='white')

    ylim(-10, +10)
    show()


def showRateCount(df):
    # 统计涨幅分布
    X = np.arange(-10, 10, 1)
    Y = list(range(-10, 10, 1))

    _index = 0
    for x in range(-10, 10, 1):
        min = x
        max = x + 1
        if x == -10:
            min = -45
            max = -9
        elif x == 9:
            min = 9
            max = 45

        print('({},{})'.format(min, max))
        _between = df[min < df['p_change']]
        _between = _between[_between['p_change'] <= max]
        Y[_index] = len(_between.index)

        _index += 1

    print(Y)
    bar(X, Y, facecolor='#9999ff', edgecolor='white')

    show()


showRateCount(df)
