# bibliotool
A set of Python utils for local library.

## How to use bibliotool 
`$ pip3 install -r requirements.txt`
### Without Docker:
```
$ sudo -i -u postgres
postgre$ psql -U postgres -a -f init.sql
```
### With Docker
```
$ sudo docker-compose -d
```
## Running utils

#### digger.py
```
usage: digger.py [-h] [-s S] [-a A] [-u]

This is an utility for adding books to database

optional arguments:
  -h, --help  show this help message and exit
  -s S        path to directory with books
  -a A        book file path
  -u          update flag, shows if you need to update path to existing books
```
Usage example: `python3 digger.py -s booksdir`

#### seeker.py
```
usage: seeker.py [-h] [-a A] [-n N] [-y Y] [-s]

This is an utility for searching books in database, prints results to stdout

optional arguments:
  -h, --help  show this help message and exit
  -a A        author name
  -n N        book name
  -y Y        book year
  -s          output only book id

```
Usage example: `python3 -a Mark Lutz`

#### wiper.py

```usage: wiper.py [-h] [-n N] [-a]

This is an utility for deleting books from database

optional arguments:
  -h, --help  show this help message and exit
  -n N        book for delete id
  -a          clean the entire database
```
Usage example: `python3 wiper.py -a` or `python3 wiper.py -n 15`
