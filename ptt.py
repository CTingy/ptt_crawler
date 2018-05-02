#!/home/sam16/anaconda3/bin/python

import requests
import time
#from datetime import datetime
from bs4 import BeautifulSoup
import os, sys
import json


PTT_URL = 'https://www.ptt.cc'


def get_web_page(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url: ', resp.url)
        return None
    else:
        return resp.text


def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'lxml')
    # 取得上一頁的連結
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']

    articles = []
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').text.strip() == date:  # 發文日期正確
            # 取得推文數
            push_count = 0
            push_str = d.find('div', 'nrec').text
            if push_str:
                try:
                    push_count = int(push_str)  # 轉換字串為數字
                except ValueError:
                    # 若轉換失敗，可能是'爆'或 'X1', 'X2', 'XX' ...
                    # 若不是, 不做任何事，push_count 保持為 0
                    if push_str == '爆':
                        push_count = 100
                    elif push_str == 'XX':
                        push_count = -100
                    elif push_str.startswith('X'):
                        push_count = int(push_str.replace('X', '-'))

            # 取得文章連結及標題
            if d.find('a'):  # 有超連結，表示文章存在，未被刪除
                href = PTT_URL + d.find('a')['href']
                title, article_time, author, content = get_content(href)
                articles.append({
                    'title': title,
                    'href': href,
                    'push_count': push_count,
                    'author': author,
                    'datetime': article_time,
                    'content': content
                })
    return articles, prev_url


def get_content(url):
    resp = requests.get(url=url)
    soup = BeautifulSoup(resp.text, 'lxml')
    
    div = soup.find_all('div', 'article-metaline')

    title = div[1].find_all('span')[1].text.strip()
    
    article_time = div[2].find_all('span')[1].text.strip()
    #dt = time.strptime(article_time, '%a %b %d %H:%M:%S %Y')

    author = div[0].find_all('span')[1].text.strip()

    target_content = u'※ 發信站: 批踢踢實業坊(ptt.cc),'
    main_content = soup.find(id='main-content').text.strip()
    content = main_content.split(article_time)[1].split(target_content)[0]
   
    return title, article_time, author, content


if __name__ == '__main__':
    url = '{}/bbs/{}/index.html'.format(PTT_URL, sys.argv[1])
    current_page = get_web_page(url)
    if current_page:
        articles = []  # 全部的今日文章
        today = time.strftime("%m/%d").lstrip('0')
        current_articles, prev_url = get_articles(current_page, today)
        
        # 若目前頁面有今日文章則加入 articles，並回到上一頁繼續尋找是否有今日文章
        while current_articles:
            articles += current_articles
            current_page = get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = get_articles(current_page, today)

        with open('ptt.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)           
