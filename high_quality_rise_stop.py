"""高质量板复盘"""
import datetime
import json
import os
import time

import pandas as pd
import redis
import requests

_redis = None
_rise_stops = {}
_rise_stop_counts = {}
_codes = []
_names = []
_counts = []
_signs = []
_urls = []


def list_it():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': 'bid=c018f745bdec43fc4a443e4eae8444de_ix8f40u5; webp=0; s=741dd8rbxa; xq_a_token=734f98bd03885fa6f46c3df71533334815e87e3a; xq_r_token=7cc627989254e3bfcbfb98b40e0d7b4664d19be3; u=7709157979; xq_token_expire=Sun%20Feb%2019%202017%2013%3A22%3A05%20GMT%2B0800%20(CST); xq_is_login=1; Hm_lvt_1db88642e346389874251b5a1eded6e3=1484213222,1484559584,1484614479,1485321715; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1485321906; __utma=1.1283382214.1482897890.1484614489.1485321907.15; __utmc=1; __utmz=1.1484203800.13.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic',
        'Host': 'xueqiu.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 FirePHP/0.7.4'
    }

    stock_rank_template = 'https://xueqiu.com/stock/cata/stocklist.json?page=1&size=60&order=desc&orderby=percent&type=11,12&_={}'
    url = stock_rank_template.format(int(time.time() * 1000))

    try:
        dom = requests.get(url=url, headers=headers)
    except Exception as e:
        print(e)
        print('请检查token')
        return

    print(url)
    r = dom.content.decode('utf-8')
    r = json.loads(r)

    if 'error_code' in r:
        print(r)
        time.sleep(1)
        return

    for x in r['stocks']:
        if float(x['current']) < get_rise_stop(x['code']):
            continue
        elif float(x['high']) == float(x['low']):
            continue
        elif x['name'].startswith('N'):
            continue

        minute_temlate = 'https://xueqiu.com/stock/forchart/stocklist.json?symbol={}&period=1d&one_min=1&_={}'
        url = minute_temlate.format(x['symbol'], int(time.time() * 1000))
        try:
            dom = requests.get(url=url, headers=headers)
        except Exception as e:
            print(e)
            print('请检查token')
            return

        minutes = dom.content.decode('utf-8')
        minutes = json.loads(minutes)

        chartlist = minutes['chartlist']

        count = 0
        growth_array = []
        pre_close = float(x['current']) - float(x['change'])
        _sum = 0
        for i in range(len(chartlist) - 1):
            diff = chartlist[i + 1]['current'] - chartlist[i]['current']
            if diff < 0:
                growth = _sum / pre_close * 100
                _sum = 0
                if growth > 1:
                    growth_array.append(growth)
                    count += 1
            else:
                _sum += diff

        # 撮合成交
        count += 1
        open_f = 1  # 撮合成交系数
        growth_array.append((chartlist[len(chartlist) - 1]['current'] - pre_close) / pre_close * 100 * open_f)

        if count == 0:
            continue

        _codes.append(x['code'])
        _names.append(x['name'])
        _counts.append(count)
        _signs.append(round(sum(growth_array) / count, 2))
        _urls.append('https://xueqiu.com/S/{}'.format(x['symbol']))

        # print(x)
        # print(url)
        print('{}, percent: {}, current: {}, rise stop: {}'.format(x['name'], x['percent'], x['current'],
                                                                   get_rise_stop(x['code'])),
              x['code'], x)

    hist = pd.DataFrame(data={'code': _codes, 'name': _names})
    hist['指标'] = _signs
    hist['count'] = _counts
    hist['url'] = _urls
    hist = hist.sort_values(['指标', 'count'], ascending=False)
    hist = hist.reset_index(drop=True)
    print(hist)

    date = str(datetime.datetime.now().date())
    # path = 'd:/analyze_data'
    path = './data/high_quality_rise_stop'
    if not os.path.exists(path):
        os.makedirs(path)
    hist.to_csv('{}/{}.csv'.format(path, date))


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
