import tushare as ts

print('hello world')

df = ts.get_hist_data('002337').head(200)
df['limit_up'] = False
df['limit_up_r'] = df['close'] * 1.1
print(df)

indexes = df.index.values
last_index = None
for x in indexes:
    if last_index is None:
        last_index = x
        df.loc[x, 'limit_up_r'] = round(df.loc[x, 'open'] * 1.1, 2)
    else:
        df.loc[x, 'limit_up_r'] = round(df.loc[last_index, 'close'] * 1.1, 2)

from pylab import *

n = len(df.index)
# X = df.index.values
X = np.arange(n)
Y1 = df['p_change'].values

bar(X, +Y1, facecolor='#9999ff', edgecolor='white')

# xlim()
ylim(-10, +10)
show()
