import argparse

import db

parser = argparse.ArgumentParser(
    description='This is an utility for deleting books from database')
parser.add_argument('-n', help='delete book by id', type=int)
parser.add_argument('-a', action='store_true', default=False,
                    help='clean the entire database')

if __name__ == '__main__':
    args = parser.parse_args()

    connection, cursor = db.get_connection()

    if args.a:
        db.delete_all(cursor)
    elif args.n:
        db.delete_by_id(cursor, args.n)

    db.close_connection(connection, cursor)
