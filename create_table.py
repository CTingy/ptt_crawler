import psycopg2


def create1():
	cur.execute('''CREATE TABLE article
	 (article_id SERIAL PRIMARY KEY,
	 title CHAR(150),
	 author CHAR(100),
	 board CHAR(50) NOT NULL,
	 content TEXT,
	 push_count INT,
	 url CHAR(150),
	 article_time TIMESTAMP)''')
	conn.commit()


def create2():
	cur.execute('''CREATE TABLE push
	 (push_id SERIAL PRIMARY KEY,
	 article_id INT REFERENCES article(article_id) ON DELETE CASCADE,
	 push_author CHAR(100) NOT NULL,
	 push_content TEXT,
	 push_state INT,
	 push_time TIMESTAMP)''')
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
	create1()
	create2()
	conn.close()

