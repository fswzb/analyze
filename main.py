import tushare as ts

print('hello world')

df = ts.get_hist_data('002337').head(200)
df['limit_up'] = False
print(df)

from pylab import *

n = len(df.index)
# X = df.index.values
X = np.arange(n)
Y1 = df['p_change'].values
# Y2 = (1-X/float(n)) * np.random.uniform(0.5,1.0,n)

bar(X, +Y1, facecolor='#9999ff', edgecolor='white')
# bar(X, -Y2, facecolor='#9999ff', edgecolor='white')

# for x,y in zip(X,Y1):
#     text(x+0.4, y+0.05, '%.2f' % y, ha='center', va= 'bottom')

# xlim()
ylim(-10,+10)
show()