import tushare as ts

print('hello world')

df = ts.get_hist_data('002337').head(200)
df['limit_up'] = False
print(df)

indexes = df.index.values
last_index = None
for x in indexes:
    if last_index is not None:
        
        pass


from pylab import *

n = len(df.index)
# X = df.index.values
X = np.arange(n)
Y1 = df['p_change'].values

bar(X, +Y1, facecolor='#9999ff', edgecolor='white')

# xlim()
ylim(-10, +10)
show()
