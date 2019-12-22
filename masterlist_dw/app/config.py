import os

class Config(object):
    pass


class DevelopmentConfig(Config):
    DEV_DATABASE = os.environ.get('DEV_DATABASE')
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@postgres_db/{}'.format(DEV_DATABASE)


class ProductionConfig(Config):
    DATABASE = os.environ.get('DATABASE')
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@postgres_db/{}'.format(DATABASE)
