import pandas as pd
import seaborn as sns

sns.set(style="white")
df = pd.DataFrame({'count': [78, 156, 74, 63, 57, 66, 61, 58, 57, 60, 64, 68, 71, 71, 68, 74, 70, 69, 75, 81, 77, 76,
                             75, 74, 72, 61, 74, 68, 72, 68, 76, 81, 76, 75, 74, 79, 79, 80, 81, 80, 83, 91, 88, 91, 92,
                             92, 94, 95, 95, 96, 93]})
# df.set_index(df['time'])
sns.pointplot(df.index, df['count'])
# sns.axlabel('time', 'count')
sns.plt.show()
