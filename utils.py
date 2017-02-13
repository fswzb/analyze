import os
from multiprocessing.pool import ThreadPool

import pandas as pd
from pandas.compat import StringIO

import tushare as ts


def get_settlement(hist):
    """计算前一日的收盘价，hist必须按时间倒序排列"""
    settlement = list(hist['close'])
    settlement.append(round(hist['open'][0] / 1.1, 2))
    settlement.pop(0)
    return settlement


def get_stock_basics():
    """获取A股所有股票基本信息，如果服务器不好用则从文件读取"""
    try:
        basics = ts.get_stock_basics()
        basics.to_csv('d:/analyze_data/all.csv')
    except:
        text = open('d:/analyze_data/all.csv', encoding='GBK').read()
        text = text.replace('--', '')
        df = pd.read_csv(StringIO(text), dtype={'code': 'object'})
        basics = df.set_index('code')
    return basics


def get_hist_data(code, start=None, end=None):
    """从文件读取日K"""
    filename = 'd:/analyze_data/k/{}.csv'.format(code)
    if os.path.exists(filename):
        text = open(filename, encoding='GBK').read()
        text = text.replace('--', '')
        df = pd.read_csv(StringIO(text), dtype={'date': 'object'})
        df = df.set_index('date')
        if start is not None:
            df = df[df.index >= start]
        if end is not None:
            df = df[df.index <= end]
        return df
    else:
        return ts.get_hist_data(code, start=start, end=end)


def get_k_data(code, date, ktype):
    """获取任意分钟K线"""

    df = ts.get_tick_data(code, date=date)
    # print(df)

    try:
        df['time'] = date + ' ' + df['time']
        df['time'] = pd.to_datetime(df['time'])
    except Exception as e:
        print(code, df['time'])
        return None

    df = df.set_index('time')
    # print(df)

    # 生成 一分钟 open high low close
    price_df = df['price'].resample('1min').ohlc()
    price_df = price_df.dropna()
    # print(price_df)

    # 累计成交额和成交量
    vols = df['volume'].resample('1min').sum()
    vols = vols.dropna()
    vol_df = pd.DataFrame(vols, columns=['volume'])

    amounts = df['amount'].resample('1min').sum()
    amounts = amounts.dropna()
    amount_df = pd.DataFrame(amounts, columns=['amount'])

    # 合并df
    try:
        min_df = price_df.merge(vol_df, left_index=True, right_index=True).merge(amount_df, left_index=True,
                                                                                 right_index=True)
    except Exception as e:
        print(code, price_df, vol_df, amount_df)
        return None
    # print(min_df)

    # 合成指定k线
    d_dict = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'amount': 'sum'}

    r_df = pd.DataFrame()
    for col in min_df:
        r_df[col] = min_df[col].resample(ktype + 'min', how=d_dict[col])
    r_df = r_df.dropna()

    # print(r_df)

    return r_df


def get_high_time(index):
    """获取股价最高时间点"""
    df = get_k_data(index, date='2017-02-03', ktype='30')
    if df is not None:
        max = df['high'].max()
        # print(df[df['high'] == max].index[0])
        print(df[df['high'] == max].head(1))


if __name__ == '__main__':
    basics = get_stock_basics()
    td = ThreadPool()
    td.map(get_high_time, basics.index)
