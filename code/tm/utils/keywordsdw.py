from sqlalchemy.orm import Session, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, Table, Column, Text, Date,
                            Integer, String, ForeignKey, Boolean)
from sqlalchemy.orm import Session, relationship, backref

Base = declarative_base()
kw_engine = create_engine('postgresql+psycopg2://likit:password@localhost/keywordsdw')
session = Session(kw_engine)


class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    word_en = Column(String(64), nullable=False, index=True)
    word_th = Column(String(64), nullable=False, index=True)
    abstract_id = Column(Integer(), ForeignKey('abstracts.id'))
    first_name = Column(String(64), nullable=False, index=True)
    last_name = Column(String(64), nullable=False, index=True)
    count = Column(Integer())
    from_keyword = Column(Boolean(), default=False)
    abstract = relationship('Abstract', backref=backref('keywords'))


class Abstract(Base):
    __tablename__ = 'abstracts'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    title_en = Column(Text())
    abstract_en = Column(Text())
    title_th = Column(Text())
    abstract_th = Column(Text())
    scopus_id = Column(String(32), nullable=False, unique=True)
    cited = Column(Integer())
    pub_date = Column(Date())


class Affiliation(Base):
    __tablename__ = 'affils'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    scopus_id = Column(String(64))
    name = Column(String())
    country = Column(String())


class AffiliationHistory(Base):
    __tablename__ = 'affil_history'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    year = Column(Integer())
    affiliation_id = Column(Integer(), ForeignKey('affils.id'))
    author_id = Column(Integer(), ForeignKey('authors.id'))
    affilation = relationship('Affiliation', backref=backref('history'))
    author = relationship('Author', backref=backref('affilations'))


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    first_name = Column(String(255))
    last_name = Column(String(255))


if __name__ == '__main__':
    Base.metadata.create_all(kw_engine)