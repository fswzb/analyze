import datetime
import tushare as ts

def explore_second_rise(hist):
    return False

if __name__ == '__main__':
    s=datetime.datetime.now()

    basics = ts.get_stock_basics()
    for index, row in basics:
        continue

    print(datetime.datetime.now()-s)