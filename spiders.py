# -*- coding: utf-8 -*-
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from functools import wraps

import pymysql
import requests
from lxml import etree
from fake_useragent import UserAgent

UA = UserAgent(path='user_agents.json')

lock = Lock()

mysql_conn = pymysql.connect(
    host="127.0.0.1",
    user='root',
    password=os.environ.get('DB_PASSWORD'),
    database='mine',
    charset='utf8'
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
    return r


def save(**kwargs):
    """ 保存数据 """

    # 如果实在多线程中执行要加锁
    # with lock:

    sql = "insert into hotrows (`data`, `data_type`, `name`) values (%s, %s, %s)"
    cursor.execute(sql, (kwargs.get('data'), kwargs.get('data_type'), kwargs.get('name')))
    mysql_conn.commit()


@logging
def get_v2ex():
    """ V2EX """

    data_type = 'V2EX'
    name = 'V2EX'
    url = 'https://www.v2ex.com/?tab=hot'
    host = 'https://www.v2ex.com'

    r = request(url, timeout=30)
    r.encoding = r.apparent_encoding
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
    r.encoding = r.apparent_encoding
    html = etree.HTML(r.text)
    hot_list = html.xpath('//div[@class="lst lst-2 hot-list"]/div/ul/li/a')

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
    headers = {
        'Cookie': '_zap=ecd79f14-bebf-44d1-a349-a5a406800fb8; _xsrf=39631860-4fe1-49f1-b760-4defb5f27b39; d_c0="AOAV1_S_6xCPTnyxu1rB-VdaAxRkflX8aEI=|1583478810"; _ga=GA1.2.127198227.1583478813; tst=h; tshl=; q_c1=4af85883e3214a879d516bf26b6ca5c9|1583808432000|1583808432000; __utma=51854390.127198227.1583478813.1584275862.1584275862.1; __utmc=51854390; __utmz=51854390.1584275862.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=51854390.100-1|2=registration_date=20141205=1^3=entry_date=20141205=1; _gid=GA1.2.2073946947.1584953899; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1584961058,1585020440,1585022753,1585031696; capsion_ticket="2|1:0|10:1585032595|14:capsion_ticket|44:YjQ2ZDUxY2Y5NDQ0NGZiOGJkMTc5ZmI5NmQ5NjQyYWI=|7d0c0042e83d5b8541db49f36b050dbc4029587a677b8c51ec40a2b70a4475e5"; z_c0="2|1:0|10:1585032601|4:z_c0|92:Mi4xOFNhckFBQUFBQUFBNEJYWDlMX3JFQ1lBQUFCZ0FsVk5tZnRtWHdEQXpySExPMnhWSmhMcWlXNkYwU1I3Wm5oUE9n|6eda3fa2500791876b2b923f124058f2e13eb78870d77177bcf8c46ce2f97b89"; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1585032602; KLBRSID=b33d76655747159914ef8c32323d16fd|1585032604|1585030527',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }

    r = request(url, headers=headers)
    r.encoding = r.apparent_encoding
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

    html = etree.HTML(request(url).text)
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
    """ GitHub """

    name = 'GitHub'
    data_type = 'github'
    url = 'https://github.com/trending'

    r = request(url)
    r.encoding = 'utf-8'
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

    r = requests.get(url)
    r.encoding = r.apparent_encoding
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
            # 执行任务 V2EX访问好慢...
            all_task = [executor.submit(func) for func in all_func]

            # 每个任务完成之后保存一下结果
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
