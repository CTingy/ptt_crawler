#!/home/sam16/anaconda3/bin/python

import requests
import time
#from datetime import datetime
from bs4 import BeautifulSoup
import os, sys
import json


PTT_URL = 'https://www.ptt.cc'


def get_web_page(url):
    try:
        resp = requests.get(
            url=url,
            cookies={'over18': '1'}
        )
        if resp.status_code == 200:
            return resp.text
        else:
            print('Wrong status code:', resp.status_code)
            return None
    except Exception as e:
        print('Cannot get web page')
        return None



def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'lxml')
    # 取得上一頁的連結
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']
    
    articles = [] # 儲存取得的文章資料
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').text.strip() == date:  # 發文日期正確
            # 取得文章連結
            if d.find('a'):  # 有超連結，表示文章存在，未被刪除
                href = PTT_URL + d.find('a')['href']
                article = get_content(href)
                articles.append(article)
    return articles, prev_url


def get_content(url):
    resp = requests.get(url=url)
    soup = BeautifulSoup(resp.text, 'lxml')

    # get article content
    div = soup.find_all('div', 'article-metaline')
    title = div[1].find_all('span')[1].text.strip()
    article_time = div[2].find_all('span')[1].text.strip()
    #dt = time.strptime(article_time, '%a %b %d %H:%M:%S %Y')
    author = div[0].find_all('span')[1].text.strip()
    target_content = u'※ 發信站: 批踢踢實業坊(ptt.cc),'
    main_content = soup.find(id='main-content').text.strip()
    content = main_content.split(article_time)[1].split(target_content)[0]
    
    # get push content 
    pushes = soup.find_all('div', 'push')
    push_list = []
    push_count = 0
    for push in pushes:
        push_author = push.find("span", "f3 hl push-userid").text
        push_content = push.find("span", "f3 push-content").text.lstrip(': ')
        push_time = push.find("span", "push-ipdatetime").text.rstrip('\n')
        push_str = push.find("span", "push-tag").text
        if push_str == '推 ' :
            push_state = 1
        elif push_str == '噓 ':
            push_state = -1
        else:
            push_state = 0
        push_count += push_state
        push_list.append({
            'push_author': push_author,
            'push_content': push_content,
            'push_time': push_time,
            'push_state': push_state,
            })

    article = {
        'title': title,
        'url': url,
        'push_count': push_count,
        'author': author,
        'datetime': article_time,
        'content': content,
        'push': push_list,
    }
    return article


if __name__ == '__main__':
    url = '{}/bbs/{}/index.html'.format(PTT_URL, sys.argv[1])
    today = time.strftime("%m/%d").lstrip('0')
    current_page = get_web_page(url)
    if current_page:
        articles = []  # 全部的今日文章
        current_articles, prev_url = get_articles(current_page, today)
        
        # 若目前頁面有今日文章則加入 articles，並回到上一頁繼續尋找是否有今日文章
        while current_articles:
            articles += current_articles
            current_page = get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = get_articles(current_page, today)

        with open('{}.json'.format(sys.argv[1]), 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)           
