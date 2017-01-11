# 新股开板
# coding=utf8
import os
import pandas as pd
import numpy as np


def get_new_stock_list():
    lst = os.listdir(u'D:\quant\history\day\data')
    for x in lst:
        code = x[0:6]
        hist = pd.read_csv('d:/quant/history/day/data/{}.csv'.format(code))

        # if hist.tail(1)['date'] > '2015/1/12':
        head = hist.head(1)
        heads = hist.head(50)
        if list(head['date'])[0] > '2015-01-12':
            print(code, head['date'])


if __name__ == '__main__':
    lst = get_new_stock_list()
