# -*- coding: utf-8 -*-
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from functools import wraps

import pymysql
import requests
from lxml import etree
from fake_useragent import UserAgent

from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_CHARSET

UA = UserAgent(path='user_agents.json')

lock = Lock()

mysql_conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    charset=MYSQL_CHARSET
)
cursor = mysql_conn.cursor()


def logging(f):
    """ 打印日志的装饰器 """

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print('执行{0}失败，错误：{1}'.format(f.__name__, str(e)))
            return None

    return wrapper


def request(url, **kwargs):
    """ 简单封装一下GET请求 """

    kwargs.setdefault('headers', {})
    kwargs['headers'].setdefault('User-Agent', UA.random)
    r = requests.get(url, **kwargs)
    r.encoding = r.apparent_encoding
    return r

@logging
def save(**kwargs):
    """ 保存数据 """

    # 多线程中执行要加锁
    # with lock:

    sql = "insert into hotrows (`data`, `data_type`, `name`) values (%s, %s, %s)"
    cursor.execute(sql, (kwargs.get('data'), kwargs.get('data_type'), kwargs.get('name')))
    mysql_conn.commit()


@logging
def get_v2ex():
    """ V2EX, 建议科(fang-)学(-zhi)上(he-)网(-xie) """

    data_type = 'V2EX'
    name = 'V2EX'
    url = 'https://www.v2ex.com/?tab=hot'
    host = 'https://www.v2ex.com'

    r = request(url, timeout=30)
    html = etree.HTML(r.text)
    hot_list = html.xpath('//a[@class="topic-link"]')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.xpath('string()'),
            'url': host + hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_ithome():
    """ IT之家"""

    data_type = 'ithome'
    name = 'IT之家'
    url = 'https://www.ithome.com/'

    r = request(url)
    html = etree.HTML(r.text)
    hot_list = html.xpath('//div[@id="rank"]/ul[2]/li/a')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.xpath('string()'),
            'url': hot.get('href')
        })

    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


def get_zhihu():
    """ 知乎热榜 """

    data_type = 'zhihu'
    name = '知乎'
    url = 'https://www.zhihu.com/hot'
    # TODO: 替换cookie
    headers = {
        'Cookie': '_zap=eb29924e-6553-4d1f-aae8-32628af6fcee; d_c0="ADBXn2kGORKPTkDkd2pvbd8IOsl9ot7m0nc=|1605844531"; '
                  '_xsrf=O536U7UC8ljni3Ce79StdsNWd4iNhOmS; '
                  'q_c1=a4a8e4b0205d4f8ea5e6679416fbf468|1617084852000|1605921020000; tshl=; tst=h; '
                  'captcha_session_v2="2|1:0|10:1621473480|18:captcha_session_v2|88'
                  ':TFcrTUd3cTN4YWNQQW5OVXRDYVlvb1hhMi9wVE1xSmhpeTF3ZzZibW5LSXhpUDdKejBjM1gxQ3A2c2FzUXpzMQ'
                  '==|a3156f767e21a50c5c094866c45596827b55393073e10187ac95f047ef634063"; '
                  '__snaker__id=i5ZcNxoSKUZVkB1b; _9755xjdesxxd_=32; '
                  'gdxidpyhxdE=LSuroE7Wve%2FbeyNZsKBfAJmRSs%5CzW5sHy2Wfu%2FGxa5qwau6XaqzEhhxgjV'
                  '%2BP21AICgptCnBBlZYxymdnP%2B%2BHcddvJ8gUj8mA0ca0iYGNDnmcWoJLoMLQEIkix6w'
                  '%2BcV6hgAqspby8Cvpo33YV4t9Ucm%2Fp9QCqER3LmZMzkgbru2qrtI%2FM%3A1621474383863; '
                  'YD00517437729195%3AWM_NI=424NjEPUsUyEC3xNq9%2BalmFY1JddXWDcFH5AFTPMe%2B%2BUGiuDVEbIwyPtCY4Is758o'
                  '%2FaSzWAZNHKIPm3950xvMp%2Fyu76b3V%2FgMPCrDH5JvKaAeR2HbgP9C6U2%2Fg8WZs7QOVY%3D; '
                  'YD00517437729195%3AWM_NIKE'
                  '=9ca17ae2e6ffcda170e2e6ee88ec4898b0999bf268a6e78eb2d44b969e9fbbae61ad8fbfabf76ff1b9ac98b82af0fea7c3b92af8eefcafe94f948bbdb6fc4f81edb8aff433e9bfa48ec553f396ac85db5d88bd8aa9b84b868ca0aee821e98b898af850969baeaaf67394ac8dbab743b1e9fbd9ee25a38db6b8c4528e9885aad367f1e7fbd1fb7e8fb0e19af83df6befdb7ae6d8f908d93c744f796baace44ba78efea9e16d94e78dd7d83aedb9f8b8d979f58f81b7dc37e2a3; YD00517437729195%3AWM_TID=mMyatKM1pudBRUARFQdvhoV7d4P3gZwo; captcha_ticket_v2="2|1:0|10:1621473488|17:captcha_ticket_v2|704:eyJ2YWxpZGF0ZSI6IkNOMzFfYVYxMHVGSWEyekw0ODJSa0l5TklCVGNIa2VyZERqWEJRVTVpMWhXb0k4X3JvdE1GbWdEcXk5ZmNPZEo3TmxCR0NzNlVhbERpLUpoOU1qejZDLlFFUGFDZFZhRmR3bVM2ZnVnLXByNTFMSWlyVi5fcXFqTnVPeWY5dlI0Q0prcjZ5Qi5GVjBYcmhyNmZQMkNmU2ZXSXd1OGRyaXlXaWktMm9JbWZDVHBTWnk5VVhiMHJPemJsdkZ6bS13SmVmazkxY2hYNGVyYzlSWnh2eHcuVFdtQVZWX0ZYajA5RjdaWWZnMUx3dDJOTC1aRzYucmhuTkRlQm1iUFp6TFBySk1qbk4yMFpKR1U5anVfdlBSSl94ZGVfSG91R01pMnlLNVJfVDZWSkhBWUR3c3pkMnV1VWxZeGpTNlZkSzg2aW5mcmhiNUtXaWdXY0ROLXV6QXNhQ2NoeXc0aTdwUVJXNDlIVFhPV3RUZm1ibzBCWlJrYnNEMUI3T2NGN0tpRWZWSTBDem9OcGZjcDVtRU5hV2ZwOG1LWEsxV0lIQ2VSNXp2TFdpZ2g1X0NZNVRsRjZLb2oyekNERGEucF9SeXlQbWVOcUV4TlZxTklfU0FpVGZDQ0J4bC1vTXpYQVdnVjlrLk1WQWVweGU5cEZ6RnQwTE1Ic3BVSVhkSkpzTS5tMyJ9|68904ab424b68957d59c3f3e0a38a99ca21efb44ba40d1ba9f702e75751040ff"; z_c0="2|1:0|10:1621473488|4:z_c0|92:Mi4xOFNhckFBQUFBQUFBTUZlZmFRWTVFaVlBQUFCZ0FsVk4wQWFUWVFCU0xwQkFyQ280VjVmNS1nXzh1MXpVQWh5ZUNR|e8963a4dfeb63a0be98ce477939218cd6fd3334fa29e3ca0995d11599418d76f"; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1622512422,1622534695,1622535858,1622600714; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1622600714; SESSIONID=FQeYPAPXDT9rMOoX7RRYf7d1fqJzXhjTjopL9adFwKz; KLBRSID=5430ad6ccb1a51f38ac194049bce5dfe|1622600715|1622600688; JOID=V1gTBUMFqt4nmoFncAbSzXbnhFZhRv27cMfFMShM--FV2cMNLg1AZkSSgmF-QgmErkI-hnmyhrSs9Qt4R3tQdHY=; osd=VFwXBk4Grtokl4JjdAXfznLjh1tiQvm4fcTBNStB-OVR2s4OKglDa0eWhmJzQQ2ArU89gn2xi7eo8Qh1RH9Ud3s=',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }

    r = request(url, headers=headers)
    html = etree.HTML(r.text)
    hot_list = html.xpath('//div[@class="HotItem-content"]/a')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.xpath('h2')[0].text,
            'url': hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_weibo():
    """ 微博热搜 """

    name = '微博'
    data_type = 'weibo'
    url = 'https://s.weibo.com/top/summary'
    host = 'https://s.weibo.com'

    html = etree.HTML(request(url).text)
    hot_list = html.xpath('//td[@class="td-02"]/a')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text,
            'url': host + hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_tieba():
    """ 百度贴吧 """

    name = '贴吧'
    data_type = 'tieba'
    url = 'http://tieba.baidu.com/hottopic/browse/topicList'

    json_data = request(url).json()
    hot_list = json_data.get('data').get('bang_topic').get('topic_list')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot['topic_name'],
            'url': hot['topic_url']
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_douban():
    """ 豆瓣小组-讨论精选 """

    name = '豆瓣'
    data_type = 'douban'
    url = 'https://www.douban.com/group/explore'
    r = request(url)
    r.encoding = 'utf-8'
    html = etree.HTML(r.text)
    hot_list = html.xpath('//div[@class="bd"]/h3/a')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text,
            'url': hot.get('href')
        })
    return {'data': json.dumps(all_data), 'data_type': data_type, 'name': name}


@logging
def get_tianya():
    """ 天涯排行 """

    name = '天涯'
    data_type = 'tianya'
    url = 'http://bbs.tianya.cn/list.jsp?item=funinfo&grade=3&order=1'

    html = etree.HTML(request(url).text)
    hot_list = html.xpath('//table/tbody/tr/td[1]/a')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text.strip(),
            'url': 'http://bbs.tianya.cn' + hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_hupu():
    """ 虎扑步行街热帖 """

    name = '虎扑'
    data_type = 'hupu'
    url = 'https://bbs.hupu.com/all-gambia'

    html = etree.HTML(request(url).text)
    hot_list = html.xpath('//span[@class="textSpan"]/a')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.get('title'),
            'url': 'https://bbs.hupu.com' + hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_github():
    """ GitHub, 网络问题可能会超时, 建议科(fang-)学(-zhi)上(he-)网(-xie) """

    name = 'GitHub'
    data_type = 'github'
    url = 'https://github.com/trending'

    r = request(url)
    html = etree.HTML(r.text)
    hot_list = html.xpath('//h1[@class="h3 lh-condensed"]/a')

    all_data = []
    for hot in hot_list:
        span = hot.xpath('span')[0]
        all_data.append({
            'title': span.text.strip() + span.tail.strip(),
            'url': 'https://github.com' + hot.get('href'),
            'desc': hot.xpath('string(../../p)').strip()
        })
    return {'data': json.dumps(all_data), 'data_type': data_type, 'name': name}


@logging
def get_baidu():
    """ 百度风云榜 """

    name = '百度'
    data_type = 'baidu'
    url = 'http://top.baidu.com/buzz?b=341&c=513&fr=topbuzz_b1'

    r = request(url)
    html = etree.HTML(r.text)
    hot_list = html.xpath('//td[@class="keyword"]/a[1]')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text.strip(),
            'url': hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_():
    """ template """

    name = ''
    data_type = ''
    url = ''

    html = etree.HTML(request(url).text)
    hot_list = html.xpath('')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text,
            'url': hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


def main():
    try:
        all_func = [
            get_v2ex, get_ithome, get_zhihu, get_weibo, get_tieba, get_douban,
            get_tianya, get_hupu, get_github, get_baidu
        ]

        # 线程池
        with ThreadPoolExecutor(min(len(all_func), 10)) as executor:
            # 线程池执行任务
            all_task = [executor.submit(func) for func in all_func]

            # 同步保存结果
            for future in as_completed(all_task):
                result = future.result()
                if result:
                    print(result)
                    save(**result)
    except:
        import traceback
        traceback.print_exc()

    finally:
        cursor.close()
        mysql_conn.close()


if __name__ == '__main__':
    # 定时执行
    main()
    # print(get_douban())