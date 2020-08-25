import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_CONN_STR')
    SCHEMA = 'production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = True
