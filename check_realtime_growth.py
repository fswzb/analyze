import json
import time

import requests

# 分钟行情
'https://xueqiu.com/stock/forchart/stocklist.json?symbol=SH603009&period=1d&one_min=1&_=1483747758603'

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
    'Cookie': 's=5s12btd50g; xq_a_token=244cab7ff8813afed93440920f85c425c302e758; xqat=244cab7ff8813afed93440920f85c425c302e758; xq_r_token=85c9992f5ee1eefb6de7468ec0985be95b17481f; xq_is_login=1; u=7709157979; xq_token_expire=Thu%20Jan%2026%202017%2015%3A58%3A49%20GMT%2B0800%20(CST); bid=c018f745bdec43fc4a443e4eae8444de_ixed8ivo; webp=0; __utma=1.484767604.1483257518.1483257518.1483710443.2; __utmb=1.4.9.1483710443; __utmc=1; __utmz=1.1483710443.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; Hm_lvt_1db88642e346389874251b5a1eded6e3=1483257518,1483710408,1483710443,1483710829; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1483711188',
    'Host': 'xueqiu.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 FirePHP/0.7.4'
}

while True:
    url = 'https://xueqiu.com/stock/cata/stocklist.json?page=1&size=60&order=desc&orderby=percent&type=11,12&_={}'.format(
        int(
            time.time() * 1000))
    dom = requests.get(url=url, headers=headers)

    print(url)
    potentions = []
    r = dom.content.decode('utf-8')
    r = json.loads(r)
    for x in r['stocks']:
        if float(x['percent']) >= 9.99:
            potentions.append(x)
    print(potentions)
    print(len(potentions))

    time.sleep(1)
