import requests
from multiprocessing import Pool
from requests.exceptions import RequestException
import re
import json

"""
author  朱培
title   爬取猫眼电影TOP100榜单电影数据

"""
def get_one_page(url):
    try:
        headers = {
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        11
        response = requests.get(url, headers=headers)
        if response.status_code ==200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
     + '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
     + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)

    items =re.findall(pattern,html)
    for item in items:
        yield {
            'index':item[0],
            'image':item[1],
            'title':item[2],
            'actor':item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }

def write_to_file(content):
    with open('movie_maoyan.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(offset):
    url ='http://maoyan.com/board/4?offset='+str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        #print(item)
        write_to_file(item)

if __name__ == '__main__':
    #for i in range(10):
    #   main(i*10)
    pool = Pool()
    pool.map(main,[i*10 for i in range(10)])

