from urllib.parse import urlencode
import pymongo
import requests
from lxml.etree import XMLSyntaxError
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq
from weixin.config import *

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

base_url = 'http://weixin.sogou.com/weixin?'

headers = {
    'Cookie':'IPLOC=CN4403; SUID=3FCE7B772F20910A000000005B260186; SUV=1529217414029695; ABTEST=0|1529217415|v1; weixinIndexVisited=1; JSESSIONID=aaacCMP6pE37i9pEkElnw; PHPSESSID=a9g8p124nlqce14o7bimje83d5; SUIR=BD4DF8F48287EC532E5EAF39830371C3; ppinf=5|1529222077|1530431677|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTozOm5ld3xjcnQ6MTA6MTUyOTIyMjA3N3xyZWZuaWNrOjM6bmV3fHVzZXJpZDo0NDpvOXQybHVLVmdzM1ZDclFGU1I0MlUwZ0NZakxzQHdlaXhpbi5zb2h1LmNvbXw; pprdig=IRkTHJI8w19Enb4S_I6AHS54Kx2EoLwGXpXhYXGTl-xLMwNuf2EzKLNdTG_LT27gvcOpwPmLm6HC4_0f8f08gCPC2zipZOS4DK1AcuCI-gWiibpgX338PxvlY3yTkjcinzMqJpoJOg4NIS_nFk2gzENIHJ7qQFJWSIBe_BKlvO0; sgid=25-35572819-AVsmE72DJIBC24o1vqRYuWk; ppmdig=15292220770000005df25898555965475f92799139b6d273; sct=3; SNUID=C6BE0A0672771CA3B661C39D72A34F49; seccodeRight=success; successCount=1|Sun, 17 Jun 2018 08:00:00 GMT',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}

proxy = None


def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url, count=1):
    print('Crawling', url)
    print('Trying Count', count)
    global proxy
    if count >= MAX_COUNT:
        print('Tried Too Many Counts')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            # Need Proxy
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print('Error Occurred', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)



def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': 2,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')

def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content').text()
        date = doc('#post-date').text()
        nickname = doc('#js_profile_qrcode > div > strong').text()
        wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None

def save_to_mongo(data):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('Saved to Mongo', data['title'])
    else:
        print('Saved to Mongo Failed', data['title'])


def main():
    for page in range(1, 101):
        html = get_index(KEYWORD, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)



if __name__ == '__main__':
    main()
