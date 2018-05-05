import psycopg2
import requests
from datetime import datetime
from bs4 import BeautifulSoup


def update(cur):
    today = datetime.now().strftime("%m/%d")
    year = datetime.now().strftime('%Y')
    
    cur.execute('SELECT article_id,url,push_count FROM article')
    articles = cur.fetchall()
    a = 0
    for article in articles:
        print(article[1].strip())
        resp = requests.get(
            url=article[1],
            cookies={'over18': '1'}
        )
        if resp.status_code != 200:
            print('Invalid url: ', resp.url)
            continue

        soup = BeautifulSoup(resp.text, 'lxml')
        pushes = soup.find_all('div', 'push')
        push_count = article[2] 
        
        for push in pushes:
            push_time = push.find("span", "push-ipdatetime").text.strip() + year
            if today in push_time:
                push_time = datetime.strptime(push_time, '%m/%d %H:%M%Y')
                push_author = push.find("span", "f3 hl push-userid").text
                push_content = push.find("span", "f3 push-content").text.lstrip(': ')
                push_str = push.find("span", "push-tag").text.strip()
                if push_str == u'推' :
                    push_state = 1
                elif push_str == u'噓':
                    push_state = -1
                else:
                    push_state = 0
                push_count += push_state
            
                cur.execute('''INSERT INTO push (
                    push_author,
                    push_content,
                    push_state,
                    push_time,
                    article_id) VALUES (%s, %s, %s, %s, %s)''', (
                    push_author,
                    push_content,
                    push_state,
                    push_time,
                    article[0])
                )
                conn.commit()

        cur.execute('UPDATE article SET push_count = %s \
            WHERE article_id = %s', (push_count, article[0]))
        conn.commit()


if __name__ == '__main__':
    conn = psycopg2.connect(
        database="testdb", 
        user="test", 
        password="test123",
        host="127.0.0.1", 
        port="5432"
    )
    cur = conn.cursor()
    update(cur)
    conn.close()
