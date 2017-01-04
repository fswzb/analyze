# 涨停
import numpy as np
import pandas as pd

# hist = pd.read_csv('d:/quant/history/day/data/000001.csv')
hist = pd.read_csv('d:/quant/history/day/data/002277.csv')
print(hist)

# 振幅
zhenfu = (hist['high'] - hist['low']) / hist['open']
print(zhenfu)

hist['zhenfu'] = zhenfu
print(hist)

# 前一天的收盘价
preclose = list(hist['close'])

preclose.reverse()  # 倒置
preclose.remove(preclose[0])  # 移除最近一天的
preclose.append(preclose[len(preclose) - 1])  # 把第一天的收盘价再次插到第0位，第一天的涨幅就算它是0
preclose.reverse()  # d倒置回来

# 涨幅
hist['growth'] = (hist['close'] - preclose) / preclose
print(hist)

hist['limitup'] = np.round(hist['growth'] * 100) / 10
print(hist)

# 涨停跌停次数
print((hist['limitup'] == 1).sum())
print((hist['limitup'] == -1).sum())
