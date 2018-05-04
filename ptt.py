import requests
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2


PTT_URL = 'https://www.ptt.cc'
BOARD = ['Soft_Job', 'TOEIC']


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


def get_articles(dom, date, b, conn):
    soup = BeautifulSoup(dom, 'lxml')
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']
    
    articles = []
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').text.strip() == date: 
            if d.find('a'): 
                href = PTT_URL + d.find('a')['href']
                article = get_content(href, b)
                save_article(article, conn)
                save_push(article['push'], conn)
                articles.append(article)
    return articles, prev_url


def get_content(url, b):
    resp = requests.get(url=url)
    soup = BeautifulSoup(resp.text, 'lxml')

    # get article content
    div = soup.find_all('div', 'article-metaline')
    title = div[1].find_all('span')[1].text.strip()
    article_time = div[2].find_all('span')[1].text.strip()
    dt = datetime.strptime(article_time, '%a %b %d %H:%M:%S %Y')
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

        now = datetime.now().strftime('%Y')
        push_time = push.find("span", "push-ipdatetime").text.strip() + now
        push_time = datetime.strptime(push_time, '%m/%d %H:%M%Y')
        push_str = push.find("span", "push-tag").text.strip()
        if push_str == u'推' :
            push_state = 1
        elif push_str == u'噓':
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
        'time': dt,
        'content': content,
        'board': b,
        'push': push_list,
    }
    return article


def connect_db():
    conn = psycopg2.connect(
    database="testdb", 
    user="test", 
    password="test123",
    host="127.0.0.1", 
    port="5432"
    )
    return conn


def save_article(article, conn):
    cur = conn.cursor()
    cur.execute('''INSERT INTO article (
        title,
        author,
        board,
        content,
        push_count,
        url,
        article_time) VALUES (%s, %s, %s, %s, %s, %s, %s)''', (
        article['title'],
        article['author'],
        article['board'],
        article['content'],
        article['push_count'],
        article['url'],
        article['time']
    ))
    conn.commit()
    

def save_push(pushes, conn):
    cur = conn.cursor()
    cur.execute('SELECT article_id FROM article \
                 ORDER BY article_id DESC LIMIT 1')
    article_id = cur.fetchall()[0][0]

    for p in pushes:
        cur.execute('''INSERT INTO push (
            push_author,
            push_content,
            push_state,
            push_time,
            article_id) VALUES (%s, %s, %s, %s, %s)''', (
            p['push_author'],
            p['push_content'],
            p['push_state'],
            p['push_time'],
            article_id)
        )
        conn.commit()


def main():
    today = datetime.now().strftime("%m/%d").lstrip('0')
    conn = connect_db()
    for b in BOARD:
        url = '{}/bbs/{}/index.html'.format(PTT_URL ,b)
        current_page = get_web_page(url)
        if current_page:
            current_articles, prev_url = get_articles(current_page, today, b, conn)
            while current_articles:
                current_page = get_web_page(PTT_URL+prev_url)
                current_articles, prev_url = get_articles(current_page, today, b, conn)
    conn.close()

    
if __name__ == '__main__':
    main()
