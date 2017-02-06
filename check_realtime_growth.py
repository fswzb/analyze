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
        'Cookie': 'bid=c018f745bdec43fc4a443e4eae8444de_ix8f40u5; webp=0; s=741dd8rbxa; xq_a_token=734f98bd03885fa6f46c3df71533334815e87e3a; xq_r_token=7cc627989254e3bfcbfb98b40e0d7b4664d19be3; u=7709157979; xq_token_expire=Sun%20Feb%2019%202017%2013%3A22%3A05%20GMT%2B0800%20(CST); xq_is_login=1; Hm_lvt_1db88642e346389874251b5a1eded6e3=1484213222,1484559584,1484614479,1485321715; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1485321906; __utma=1.1283382214.1482897890.1484614489.1485321907.15; __utmc=1; __utmz=1.1484203800.13.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic',
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
        except Exception as e:
            print(e)
            print('请检查token')
            continue

        print(url)
        potentials = []
        r = dom.content.decode('utf-8')
        r = json.loads(r)

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
    global _redis
    pool = redis.ConnectionPool(host='127.0.0.1', port='6379')
    _redis = redis.Redis(connection_pool=pool)

    list_it()
