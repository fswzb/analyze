import datetime

import pandas as pd
from pandas.compat import StringIO

import tushare as ts

if __name__ == '__main__':
    now = datetime.datetime.now()
    today = str(now.date())

    sh = ts.get_hist_data('sh')
    filename = 'data/scan_big_bid/{}.csv'.format(sh.index[0] if sh.index[0] != today else sh.index[1])

    print(filename)
    text = open(filename, encoding='GBK').read()
    text = text.replace('--', '')
    df = pd.read_csv(StringIO(text), dtype={'code': 'object'})
    hist = df.set_index('code')
    # hist = hist.head(10)
    # hist = hist.tail(10)
    print(hist)

    all = ts.get_today_all()
    all_index = list(all['code'])
    filterd = pd.DataFrame()
    for i in range(len(hist)):
        index = all_index.index(hist.index[i])
        row = all.loc[index]
        if row['volume'] > 0:
            # print(row)
            row['url'] = hist['url'][i]
            row['prehigh'] = hist['high'][i]
            filterd = filterd.append(row)

    now = pd.DataFrame({'code': filterd['code']})
    now['name'] = filterd['name']
    now['prehigh'] = filterd['prehigh']
    now['settlement'] = filterd['settlement']
    now['open'] = filterd['open']
    now['openpercent'] = ((filterd['open'] - filterd['prehigh']) / filterd['prehigh'] * 100).round(3)
    now['changepercent'] = ((filterd['trade'] - filterd['prehigh']) / filterd['prehigh'] * 100).round(3)
    now['url'] = filterd['url']
    now = now.reset_index(drop=True)
    # now = now.sort_values('openpercent')
    now = now.sort_values('changepercent')

    open_positive = (now['openpercent'] > 0).sum() / len(now) * 100
    open_avg = now['openpercent'].mean()
    now_positive = (now['changepercent'] > 0).sum() / len(now) * 100
    now_avg = now['changepercent'].mean()

    print(now)
    print('open正收益概率：{}%'.format(round(open_positive, 2)))
    print('open综合收益：{}%'.format(round(open_avg, 2)))
    print('now正收益概率：{}%'.format(round(now_positive, 2)))
    print('now综合收益：{}%'.format(round(now_avg, 2)))
