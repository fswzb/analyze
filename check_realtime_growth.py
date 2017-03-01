"""选择当前可打的板"""
import json
import time

import redis
import requests

_redis = None
_rise_stops = {}
_rise_stop_counts = {}


def list_it():
    # 涨幅榜
    'https://xueqiu.com/stock/cata/stocklist.json?page=1&size=60&order=desc&orderby=percent&type=11,12&_=1486352866218'
    # 详情
    'https://xueqiu.com/v4/stock/quote.json?code=SH600000&_=1486357136757'
    # 分钟行情
    'https://xueqiu.com/stock/forchart/stocklist.json?symbol=SH603009&period=1d&one_min=1&_=1483747758603'
    # 盘口
    'https://xueqiu.com/stock/pankou.json?symbol=SH600000&_=1486352626983'

    headers = {
        # 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Accept-Encoding': 'gzip, deflate',
        # 'Host': 'www.lagou.com',
        # 'Origin': 'http://www.lagou.com',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
        # 'X-Requested-With': 'XMLHttpRequest',
        # 'Referer': 'http://www.lagou.com',
        # 'Proxy-Connection': 'keep-alive',
        # 'X-Anit-Forge-Code': '0',
        # 'X-Anit-Forge-Token': None

        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-US,en;q=0.8',
        # 'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'bid=c018f745bdec43fc4a443e4eae8444de_ix8f40u5; webp=0; s=741dd8rbxa; xq_token_expire=Mon%20Mar%2020%202017%2010%3A37%3A45%20GMT%2B0800%20(CST); __utma=1.1283382214.1482897890.1488156701.1488181940.71; __utmz=1.1484203800.13.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; aliyungf_tc=AQAAAM2yxCvdKw4AGq72OjntYxUtrDdT; remember=1; remember.sig=K4F3faYzmVuqC0iXIERCQf55g2Y; xq_a_token=8aa48a9a84495422366f79723131c8c0343dab42; xq_a_token.sig=RbWi6_FqVqHZgNPRLMSYgjGu5SA; xq_r_token=a2c67b6bdabab97e0d2868da11476a3ff2481e70; xq_r_token.sig=e4yWmVDzf6LPlYg2x-f81LtO8-c; xq_is_login=1; xq_is_login.sig=J3LxgPVPUzbBg3Kee_PquUfih7Q; u=7709157979; u.sig=ys5wEHAJBLj9TM-BQZNyvcdpgh8; Hm_lvt_1db88642e346389874251b5a1eded6e3=1488155577,1488156795,1488156805,1488265311; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1488265341',
        'Host': 'xueqiu.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 FirePHP/0.7.4'
    }

    while True:
        url = 'https://xueqiu.com/stock/cata/stocklist.json?page=1&size=60&order=desc&orderby=percent&type=11,12&_={}'.format(
            int(
                time.time() * 1000))

        try:
            dom = requests.get(url=url, headers=headers)
            r = dom.content.decode('utf-8')
            r = json.loads(r)
        except Exception as e:
            print(e)
            print('请检查token')
            continue

        print(url)
        potentials = []

        if 'error_code' in r:
            print(r)
            time.sleep(1)
            continue

        for x in r['stocks']:
            if float(x['name'].startswith('N')):  # 新股不考虑
                continue
            elif float(x['percent']) < 8.0:  # 没启动不考虑
                continue
            # elif float(x['percent']) >= 9.99:  # 已经涨停的买不进
            #     continue
            elif float(x['high']) >= get_rise_stop(x['code']) or 0 == get_rise_stop(x['code']):  # 新股或开板股不考虑
                continue
            # elif get_rise_stop_count(x['code']) > 0:  # 三日内板过不考虑
            #     continue
            elif False:  # todo 成交量太大的不考虑
                continue
            elif False:  # todo 非龙头不考虑，不是龙头很有可能最高回落
                continue

            potentials.append(x)
            print('{}, percent: {}, current: {}, rise stop: {}'.format(x['name'], x['percent'], x['current'],
                                                                       get_rise_stop(x['code'])),
                  x['code'], x)
        print(len(potentials))

        time.sleep(1)


def get_rise_stop(code):
    global _redis, _rise_stops
    if code in _rise_stops:
        return _rise_stops[code]
    else:
        rise_stop = _redis.get('quant.{}.rise_stop'.format(code))
        rise_stop = 0 if rise_stop is None else float(rise_stop)
        _rise_stops[code] = rise_stop
        return rise_stop


def get_rise_stop_count(code):
    global _redis, _rise_stop_counts
    if code in _rise_stop_counts:
        r = _rise_stop_counts[code]
    else:
        r = _redis.get('quant.{}.rise_stop_count'.format(code))
        r = 1 if r is None else int(r)
        _rise_stop_counts[code] = r

    return int(r)


if __name__ == '__main__':
    # global _redis
    pool = redis.ConnectionPool(host='127.0.0.1', port='6379')
    _redis = redis.Redis(connection_pool=pool)

    list_it()
