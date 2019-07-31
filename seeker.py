import argparse

import db

parser = argparse.ArgumentParser(
    description='This is an utility for searching books in database, \
        prints results to stdout')
parser.add_argument('-a', help='author name')
parser.add_argument('-n', help='book name')
parser.add_argument('-y', help='book year', type=int)
parser.add_argument('-s', action='store_true', default=False,
                    help='output only book id')

if __name__ == '__main__':
    args = parser.parse_args()

    query = {}
    if args.a:
        query['author'] = args.a
    if args.n:
        query['name'] = args.n
    if args.y:
        query['year'] = args.y

    if query:
        connection, cursor = db.get_connection()
        query = [f"{k} = '{query[k]}'" for k in query]
        db.search_book(cursor, query, args.s)
        db.close_connection(connection, cursor)
