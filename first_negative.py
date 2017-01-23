# 首阴战法
import datetime

import tushare as ts


def is_growth_form(hist):
    '''多头排列'''
    if len(hist) < 2:
        return False

    ma5 = hist['ma5']
    ma10 = hist['ma10']
    ma20 = hist['ma20']
    if ma5[1] > ma10[1] > ma20[1]:
        if ma5[0] > ma10[0] > ma20[0]:
            if ma5[1] > ma5[0] and ma10[1] > ma10[0] and ma20[1] > ma20[0]:
                return True
    return False


def is_first_negative(hist):
    '''
    跌幅达到10%~15%
    西部建设、太阳电缆、新亚制程、利君股份
    '''
    # todo 跌幅达到10%~15%
    pass


def is_block_head(hist):
    '''是否是板块龙头'''
    # todo 龙头股检测
    pass


def explore_growth_form(hist):
    from_index = -1
    for index, row in hist:
        if index < from_index:
            continue

        _filter = list(index <= hist.index < index + 3)
        if is_growth_form(hist[_filter]):
            pass


if __name__ == '__main__':
    s = datetime.datetime.now()

    basics = ts.get_stock_basics()
    for code in basics.index:
        hist = ts.get_hist_data(code)
        explore_growth_form(hist)

    print(datetime.datetime.now() - s)
