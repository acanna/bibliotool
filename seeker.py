import argparse

import db

parser = argparse.ArgumentParser(
    description='This is an utility for searching books in database')
parser.add_argument('-a', help='author name')
parser.add_argument('-n', help='book name')
parser.add_argument('-y', help='book year', type=int)
parser.add_argument('-s', action='store_true', default=False,
                    help='output only book id')
args = parser.parse_args()

query = {}
if args.a:
    query['author'] = args.a
if args.n:
    query['name'] = args.n
if args.y:
    query['year'] = args.y

if query:
    conn = db.connect()
    cur = conn.cursor()

    query = [f"{k} = '{query[k]}'" for k in query]

    cur.execute(f'''SELECT * FROM Book WHERE {' AND '.join(query)}''')

    for x in cur.fetchall():
        if args.s:
            print(x[0])
        else:
            print(x)
