import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = sa.create_engine('postgresql+psycopg2://postgres@postgres_db/stagedb')

from .stg_scopuspubs import *
