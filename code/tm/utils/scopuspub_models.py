"""Database models for the Scopus article database.

"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, Table, Column, Text, Date,
                        Integer, String, ForeignKey, Boolean)
from sqlalchemy.orm import Session, relationship, backref, sessionmaker
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()
engine = create_engine('postgresql+psycopg2://postgres@postgres_db/scopuspubs')
Session = sessionmaker(bind=engine)
session = Session()


class Pub(Base):
    __tablename__ = 'pubs'
    id = Column('id', Integer, primary_key=True)
    pub_date = Column('pub_date', Date())
    cited_count = Column('cited_count', Integer(), default=0)
    data = Column('data', JSON())


if __name__ == '__main__':
    Base.metadata.create_all(engine)
