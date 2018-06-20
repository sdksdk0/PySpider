import requests
from requests.exceptions import RequestException
import re
import json
"""
author  朱培
title   爬取淘票票正在热映的电影数据

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

    pattern = re.compile('<div class="movie-card-poster">.*?data-src="(.*?)".*?<span class="bt-l">(.*?)</span>.*?<span class="bt-r">(.*?)</span>.*?<div class="movie-card-list">.*?<span>(.*?)</span>'
    +'.*?<span>(.*?)</span>.*?<span>(.*?)</span>.*?<span>(.*?)</span>.*?<span>(.*?)</span>.*?<span>(.*?)</span>',re.S)

    items = re.findall(pattern, html)
    for item in items:
        yield {
            'image': item[0],
            'title': item[1],
            'score': item[2],
            'director': item[3].strip()[3:],
            'actor': item[4].strip()[3:],
            'type': item[5].strip()[3:],
            'area': item[6].strip()[3:],
            'language': item[7].strip()[3:],
            'time': item[8].strip()[3:]
        }


def write_to_file(content):
    with open('movie_taopiaopiao.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main():
    url ='https://www.taopiaopiao.com/showList.htm'
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)

if __name__ == '__main__':
       main()
