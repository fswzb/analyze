import tushare as ts


# print(ts.get_hist_data())
# print(ts.get_suspended())
# print(ts.get_terminated())

def question():
    i = 1
    while True:
        print(i)
        if i % 2 == 1:
            if i % 3 == 0:
                if i % 4 == 1:
                    if i % 5 == 4:
                        if i % 6 == 3:
                            if i % 7 == 0:
                                if i % 8 == 1:
                                    if i % 9 == 0:
                                        break
        i += 1
    print('answer', i)


if __name__ == '__main__':
    basics = ts.get_stock_basics()
    basics = basics.sort_values('outstanding')
    print(basics)

    outstanding = basics['outstanding']
    print(outstanding)
    print(len(outstanding), outstanding.mean())

    min_and_middle = basics
    min_and_middle = min_and_middle[min_and_middle['outstanding'] < 7]  # 流通股本7亿以下
    min_and_middle = min_and_middle[min_and_middle['liquidAssets'] < 100 * 10000]  # 流通市值100亿以内
    print(min_and_middle)
    print(len(min_and_middle), min_and_middle['outstanding'].mean())

    # question()
