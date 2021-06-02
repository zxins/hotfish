# -*- coding: utf-8 -*-
import os

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASS')
MYSQL_PORT = 3306
MYSQL_DB = 'test'
MYSQL_CHARSET = 'UTF8MB4'

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://" \
                          f"{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset={MYSQL_CHARSET}"

SQLALCHEMY_TRACK_MODIFICATIONS = False
