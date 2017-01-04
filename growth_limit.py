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

preclose.reverse()
preclose.remove(preclose[0])
preclose.append(preclose[len(preclose) - 1])
preclose.reverse()

hist['preclose'] = np.array(preclose)
print(hist)

# 涨幅
hist['growth'] = (hist['close'] - hist['preclose']) / hist['preclose']
print(hist)
