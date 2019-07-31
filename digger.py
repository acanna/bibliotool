import argparse
import gzip
import itertools
import math
import multiprocessing
import os
import xml.etree.ElementTree as ET
import zipfile

import dateparser
import psutil

import db

parser = argparse.ArgumentParser(
    description='This is an utility for adding books to database')
parser.add_argument('-s', help='path to directory with books')
parser.add_argument('-a', help='book file path')
parser.add_argument(
    '-u', action='store_true', default=False,
    help='update flag, shows if you need to update path to existing books')


def parse_book(book_path):
    if book_path.endswith('fb2'):
        for event, elem in ET.iterparse(book_path,
                                        events=('end', 'end-ns')):
            if elem and elem.tag.endswith('title-info'):
                root = elem
                break
    else:
        if book_path.endswith('.zip'):
            book_file = zipfile.ZipFile(book_path)
            book_file = book_file.open(book_file.namelist()[0])
        elif book_path.endswith('.gz'):
            book_file = gzip.open(book_path, 'r')

        text = []
        while book_file.readable():
            line = book_file.readline().decode('utf-8')
            text.append(line)
            if '</title-info>' in line:
                break
        text = ''.join(text)

        parser = ET.XMLPullParser(['start'])
        parser.feed(text)
        for event, elem in parser.read_events():
            if elem and elem.tag.endswith('title-info'):
                root = elem

    def find_tags(elem, title, author, year):
        tag = elem.tag.lower()
        if not title and 'book-title' in tag:
            title = elem.text
            return title, author, year
        if not author and 'author' in tag:
            author = ' '.join(
                filter(lambda x: x, [elem[0].text, elem[1].text]))
            return title, author, year
        if not year and 'date' in tag:
            year = elem.attrib[
                'value'] if 'value' in elem.attrib else elem.text
            return title, author, year

        for child in elem:
            if not all([title, author, year]):
                title, author, year = find_tags(child, title, author, year)
        return title, author, year

    title, author, year = find_tags(root, None, None, None)
    year = dateparser.parse(year).year if year else None
    return (title, author, year), book_path


def parse_books(book_paths):
    return [parse_book(path) for path in book_paths]


def delete_duplicates(book_infos):
    for x, y in dict(book_infos).items():
        yield (*x, y)


if __name__ == '__main__':
    args = parser.parse_args()

    book_paths = []
    if args.a:
        if os.path.isfile(args.a):
            if args.a.endswith('.fb2') or args.a.endswith(
                    '.fb2.zip') or args.a.endswith('.fb2.gz'):
                book_paths.append(args.a)
        else:
            print(f'File "{args.a}" does not exist')
    if args.s:
        if os.path.isdir(args.s):
            for dirname, subdirs, files in os.walk(args.s):
                if not dirname.endswith('/'):
                    dirname += '/'
                for file in files:
                    if file.endswith('.fb2') or file.endswith(
                            '.fb2.zip') or file.endswith('.fb2.gz'):
                        book_paths.append(dirname + file)
        else:
            print(f'Directory "{args.s}" does not exist')

    if book_paths:
        num_cpus = psutil.cpu_count(logical=True)
        pool = multiprocessing.Pool(num_cpus)

        data = [None] * num_cpus
        k = math.ceil(len(book_paths) / num_cpus)
        for i in range(num_cpus):
            data[i] = book_paths[i * k: (i + 1) * k]

        books_data = itertools.chain.from_iterable(pool.map(parse_books, data))
        books_data = delete_duplicates(books_data)

        connection, cursor = db.get_connection()

        if args.u:
            db.insert_update(cursor, books_data)
        else:
            db.insert_do_nothing(cursor, books_data)

        db.close_connection(connection, cursor)
