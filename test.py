import tushare as ts

# print(ts.get_hist_data())
# print(ts.get_suspended())
# print(ts.get_terminated())



if __name__ == '__main__':
    basics = ts.get_stock_basics()
    basics = basics.sort_values('outstanding')
    print(basics)

    outstanding = basics['outstanding']
    print(outstanding)
    print(len(outstanding), outstanding.mean())

    min_and_middle = outstanding[outstanding < 5]  # 流通股本5亿以下
    print(min_and_middle)
    print(len(min_and_middle), min_and_middle.mean())

    # tp = ThreadPool()
    # r = tp.map(get_random, [random(), random(), random(), random()])
    # print(r)
