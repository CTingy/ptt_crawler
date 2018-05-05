import psycopg2


def connect_db():
    conn = psycopg2.connect(
        database="testdb", 
        user="test", 
        password="test123",
        host="127.0.0.1", 
        port="5432"
    )
    return conn
