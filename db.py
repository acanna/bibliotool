import configparser
import os

import psycopg2
import psycopg2.extras


def get_connection():
    user = 'postgres'
    password = 'postgres'
    host = 'localhost'

    if os.path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if 'psql' in config:
            if 'user' in config['psql']:
                user = config['psql']['user']
            if 'password' in config['psql']:
                password = config['psql']['password']
            if 'host' in config['psql']:
                host = config['psql']['host']

    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host
        )
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        raise

    return conn, conn.cursor()


def close_connection(conn, cur):
    if conn:
        conn.commit()
        cur.close()
        conn.close()


def delete_all(cur):
    cur.execute('DELETE FROM Book')
    print(cur.statusmessage)


def delete_by_id(cur, book_id):
    cur.execute(f'DELETE FROM Book WHERE id = {book_id}')
    print(cur.statusmessage)


def search_book(cur, query, only_id):
    cur.execute(f'''SELECT * FROM Book WHERE {' AND '.join(query)}''')
    print(cur.statusmessage)
    for x in cur.fetchall():
        if only_id:
            print(x[0])
        else:
            print(x)


def insert_do_nothing(cur, books_data):
    psycopg2.extras.execute_values(
        cur,
        '''INSERT INTO Book(name, author, year, path) VALUES %s
ON CONFLICT (path) DO NOTHING''',
        books_data,
        page_size=1000
    )
    print(cur.statusmessage)


def insert_update(cur, books_data):
    psycopg2.extras.execute_values(
        cur,
        '''INSERT INTO Book(name, author, year, path) VALUES %s
ON CONFLICT (path) DO UPDATE 
SET path = excluded.path''',
        books_data,
        page_size=1000
    )
    print(cur.statusmessage)
