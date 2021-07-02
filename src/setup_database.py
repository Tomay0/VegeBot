import psycopg2
from os import getenv
from time import sleep
import requests


def wait_for_database(num_tries=20):
    n = 0
    while True:
        try:
            return requests.head(getenv('POSTGREST_URL'))
        except requests.exceptions.ConnectionError:
            sleep(1)
            n += 1
            if n >= num_tries:
                raise RuntimeError("Could not connect to PostgREST")


def migrate():
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
