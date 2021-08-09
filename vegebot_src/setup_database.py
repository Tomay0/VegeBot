import psycopg2
from os import getenv
from time import sleep

def setup():
    for i in range(5):
        try:
            conn = psycopg2.connect(
                host=getenv('POSTGRES_HOST'),
                database=getenv('POSTGRES_DB'),
                user=getenv('POSTGRES_USER'),
            )
            break
        except:
            print('cant connect to db. Retrying in 5s...')
            sleep(5)
    else: # never connected
        print("could not connect to db")
        exit()

    cur = conn.cursor()
    with open('init.sql') as sql_init_file:
        cur.execute(sql_init_file.read())
    conn.commit()
    cur.close()
    conn.close()
