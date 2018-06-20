import requests
from multiprocessing import Pool
from requests.exceptions import RequestException
import re
import json
"""
author  朱培
title   爬取美团(深圳)美食店铺信息,评分大于4.0分的店铺

"""
def get_one_page(url):
    try:
        headers = {
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

        response = requests.get(url, headers=headers)
        if response.status_code ==200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):

    pattern = re.compile('"poiId":(.*?),"frontImg":"(.*?)","title":"(.*?)","avgScore":(.*?),"allCommentNum":(.*?)'
    +',"address":"(.*?)","avgPrice":(.*?),', re.S)

    items = re.findall(pattern, html)
    for item in items:
        if float(item[3]) >= 4.0:
            yield {
                'poiId': item[0],
                'frontImg': item[1],
                'title': item[2],
                'avgScore': item[3],
                'allCommentNum':item[4],
                'address': item[5],
                'avgPrice': item[6]
            }


def write_to_file(content):
    with open('food-meituan.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(n):
    url ='http://sz.meituan.com/meishi/pn'+str(n)+'/'
    html = get_one_page(url)

    for item in parse_one_page(html):
        print(item)
        write_to_file(item)

if __name__ == '__main__':
    #for i in range(32):
    #     main(i)
    pool = Pool()
    pool.map(main, [ 1 for i in range(32)])
