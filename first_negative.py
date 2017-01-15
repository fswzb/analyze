# 首阴战法
import datetime

import tushare as ts


def is_growth_form(hist):
    '''多头排列达到五天'''
    pass


def is_first_negative(hist):
    '''跌幅达到10%~15%'''
    pass


def is_block_head(hist):
    '''是否是板块龙头'''
    pass


if __name__ == '__main__':
    s = datetime.datetime.now()

    basics = ts.get_stock_basics()
    for code in basics.index:
        hist = ts.get_h_data(code)
        if not is_growth_form(hist):
            continue

    print(datetime.datetime.now() - s)
