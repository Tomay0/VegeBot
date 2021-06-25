import psycopg2
from os import getenv

def setup():
    conn = psycopg2.connect(
        host=getenv('POSTGRES_HOST'),
        database=getenv('POSTGRES_DB'),
        user=getenv('POSTGRES_USER'),
        password=getenv('POSTGRES_PASSWORD'))

    cur = conn.cursor()
    with open('init.sql') as sql_init_file:
        cur.execute(sql_init_file.read())
    conn.commit()
    cur.close()
    conn.close()


