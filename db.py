import configparser
import os

import psycopg2


def connect():
    if os.path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return psycopg2.connect(user=config['psql']['user'],
                                password=config['psql']['pwd'],
                                host=config['psql']['host']
                                )
    else:
        return psycopg2.connect(user='postgres',
                                password='postgres',
                                host='localhost'
                                )
