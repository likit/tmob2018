"""Database models for the Scopus article database.

"""

from sqlalchemy import (create_engine, Table, Column, Text, Date,
                        Integer, String, ForeignKey, Boolean)
from sqlalchemy.orm import Session, relationship, backref
from sqlalchemy.dialects.postgresql import JSON
from . import Base


class Pub(Base):
    __tablename__ = 'pubs'
    id = Column('id', Integer, primary_key=True)
    scopus_id = Column('scopus_id', String(32), index=True)
    doctype = Column('doctype', String(8))
    pub_date = Column('pub_date', Date())
    cited_count = Column('cited_count', Integer(), default=0)
    data = Column('data', JSON())


if __name__ == '__main__':
    Base.metadata.create_all(engine)
