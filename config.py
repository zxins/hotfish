# -*- coding: utf-8 -*-
import os

DB_PASSWORD = os.environ.get('DB_PASSWORD')

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:{0}@localhost:3306/mine?charset=utf8".format(DB_PASSWORD)

SQLALCHEMY_TRACK_MODIFICATIONS = False
