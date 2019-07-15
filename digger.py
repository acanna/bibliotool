import argparse
import gzip
import itertools
import multiprocessing
import os
import xml.etree.ElementTree as ET
import zipfile

import dateparser
import psutil

import db

os.system('sudo service postgresql start')

parser = argparse.ArgumentParser(
    description='This is an utility for adding books in database')
parser.add_argument('-s', help='directory path')
parser.add_argument('-a', help='book path')
parser.add_argument('-u', action='store_true', default=False,
                    help='update information')
args = parser.parse_args()
books = []
if args.a:
    books.append(args.a)
if args.s:
    for dirname, subdirs, files in os.walk(args.s):
        if not dirname.endswith('/'):
            dirname += '/'
        for file in files:
            if file.endswith('.fb2') or file.endswith(
                    '.fb2.zip') or file.endswith('.fb2.gz'):
                books.append(dirname + file)


def get_info(book):
    if book.endswith('fb2'):
        for event, elem in ET.iterparse(book,
                                        events=('end', 'end-ns')):
            if elem and elem.tag.endswith('title-info'):
                root = elem
                break
    else:
        if book.endswith('.zip'):
            book = zipfile.ZipFile(book)
            book = book.open(book.namelist()[0])
        elif book.endswith('.gz'):
            book = gzip.open(book, 'r')
        text = []
        while book.readable():
            line = book.readline().decode('utf-8')
            text.append(line)
            if '</title-info>' in line:
                break

        text = ''.join(text)
        parser = ET.XMLPullParser(['start'])
        parser.feed(text)
        for event, elem in parser.read_events():
            if elem and elem.tag.endswith('title-info'):
                root = elem

    title, author, year = None, None, None

    def find_tags(elem):
        nonlocal title, author, year
        tag = elem.tag.lower()
        if not title and 'book-title' in tag:
            title = elem.text
            return
        if not author and 'author' in tag:
            author = ' '.join(
                filter(lambda x: x, [elem[0].text, elem[1].text]))
            return
        if not year and 'date' in tag:
            year = elem.attrib[
                'value'] if 'value' in elem.attrib else elem.text
            return

        for child in elem:
            if not all([title, author, year]):
                find_tags(child)

    find_tags(root)
    year = dateparser.parse(year).year if year else -1
    return title, author if author else '', year


def get_infos(books):
    return [get_info(book) for book in books]


num_cpus = psutil.cpu_count(logical=True)

pool = multiprocessing.Pool(num_cpus)

data = [None] * num_cpus
k = len(books) // num_cpus
for i in range(num_cpus - 1):
    data[i] = books[i * k: (i + 1) * k]
data[-1] = books[(num_cpus - 1) * k:]

results = pool.map(get_infos, data)

books = zip(list(itertools.chain.from_iterable(results)), books)

conn = db.connect()
cur = conn.cursor()

if args.u:
    books = dict(books)
    cur.execute(f'''INSERT INTO Book(name, author, year, path)
VALUES {', '.join(map(lambda x: str((*x[0], x[1])), books.items()))}
ON CONFLICT (name, author, year) DO UPDATE
    SET path = excluded.path''')
else:
    cur.execute(f'''INSERT INTO Book(name, author, year, path)
VALUES {', '.join(map(lambda x: str((*x[0], x[1])), books))}
ON CONFLICT (name, author, year) DO NOTHING''')

conn.commit()
