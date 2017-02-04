import pandas as pd

import tushare as ts


def get_k_data(code, date, ktype):
    '''获取任意分钟k线'''

    df = ts.get_tick_data(code, date=date)
    # print(df)

    df['time'] = date + ' ' + df['time']
    df['time'] = pd.to_datetime(df['time'])

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
    min_df = price_df.merge(vol_df, left_index=True, right_index=True).merge(amount_df, left_index=True,
                                                                             right_index=True)
    # print(min_df)

    # 合成指定k线
    d_dict = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'amount': 'sum'}

    r_df = pd.DataFrame()
    for col in min_df:
        r_df[col] = min_df[col].resample(ktype + 'min', how=d_dict[col])
    r_df = r_df.dropna()

    # print(r_df)

    return r_df


if __name__ == '__main__':
    for i in range(3000):
        df = get_k_data('600000', date='2010-12-13', ktype='30')
        max = df['high'].max()
        print(df[df['high'] == max].index[0])
