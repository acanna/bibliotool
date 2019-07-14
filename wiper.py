import argparse

import db

parser = argparse.ArgumentParser(
    description='This is an utility for deleting books from database')
parser.add_argument('-n', help='book id', type=int)
parser.add_argument('-a', action='store_true', default=False,
                    help='clean the database')
args = parser.parse_args()

conn = db.connect()
cur = conn.cursor()

if args.a:
    cur.execute('TRUNCATE TABLE Book')
elif args.n:
    cur.execute(f'DELETE FROM Book WHERE id = {args.n}')

conn.commit()
