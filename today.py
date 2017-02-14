"""当日大盘分析"""
import tushare as ts

if __name__ == '__main__':
    today = ts.get_today_all()

    total = len(today)
    positive = (today['changepercent'] > 0).sum()

    p7 = today['changepercent'].ge(7).sum()
    p3 = today['changepercent'].between(3, 6.9999).sum()
    p0 = today['changepercent'].between(0.0001, 2.9999).sum()
    n0 = today['changepercent'].between(-2.9999, 0).sum()
    n3 = today['changepercent'].between(-6.9999, -3).sum()
    n7 = today['changepercent'].le(-7).sum()

    assert p7 + p3 + p0 + n0 + n3 + n7 == total

    print('')
    print('涨幅7%~10%：    {}'.format(p7))
    print('涨幅3%~7%：     {}'.format(p3))
    print('涨幅0%~3%：     {}'.format(p0))
    print('涨幅-3%~0%：    {}'.format(n0))
    print('涨幅-7%~-3%：   {}'.format(n3))
    print('涨幅-10%~-7%：  {}'.format(n7))
    print('一共{}只股票'.format(total))
    print('上涨{}只，占比{}%'.format(positive, round(positive / total * 100, 2)))
