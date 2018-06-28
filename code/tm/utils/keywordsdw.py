from sqlalchemy.orm import Session, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, Table, Column, Text, Date,
                            Integer, String, ForeignKey, Boolean)
from sqlalchemy.orm import Session, relationship, backref

Base = declarative_base()
kw_engine = create_engine('postgresql+psycopg2://likit:password@localhost/keywordsdw')
session = Session(kw_engine)

nounchunk_has_keyword = Table('nounchunk_has_keyword', Base.metadata,
    Column('noun_chunk_id', Integer, ForeignKey('noun_chunks.id')),
    Column('keyword_id', Integer, ForeignKey('keywords.id'))
)

field_has_abstract = Table('field_has_abstract', Base.metadata,
    Column('field_id', Integer, ForeignKey('research_fields.id')),
    Column('abstract_id', Integer, ForeignKey('abstracts.id'))
)

abstract_has_nounchunk = Table('abstract_has_nounchunk', Base.metadata,
    Column('abstract_id', Integer, ForeignKey('abstracts.id')),
    Column('noun_chunk_id', Integer, ForeignKey('noun_chunks.id'))
)

abstract_has_keywords = Table('abstract_has_keywords', Base.metadata,
    Column('abstract_id', Integer, ForeignKey('abstracts.id')),
    Column('keyword_id', Integer, ForeignKey('keywords.id'))
)

abstract_has_author = Table('abstract_has_author', Base.metadata,
    Column('abstract_id', Integer, ForeignKey('abstracts.id')),
    Column('author_id', Integer, ForeignKey('authors.id'))
)

class ResearchField(Base):
    __tablename__ = 'research_fields'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(255))
    abbr = Column(String(8))
    scopus_id = Column(String())
    abstracts = relationship('Abstract', secondary=field_has_abstract,
                                backref='fields')


class NounChunk(Base):
    __tablename__ = 'noun_chunks'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    chunk_en = Column(String(255), nullable=False)
    chunk_th = Column(String(255), nullable=False)
    abstracts = relationship('Abstract', secondary=abstract_has_nounchunk,
                                backref='noun_chunks')
    keywords = relationship('Keyword', secondary=nounchunk_has_keyword,
                                backref='noun_chunks')


class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    word_en = Column(String(64), nullable=False, index=True)
    word_th = Column(String(64), nullable=False, index=True)
    abstract_id = Column(Integer(), ForeignKey('abstracts.id'))
    first_name = Column(String(64), index=True)
    last_name = Column(String(64), index=True)
    count = Column(Integer())
    author_scopus_id = Column(String(64))
    affil_scopus_id = Column(String(32))
    abstracts = relationship('Abstract', backref=backref('keywords'),
                        secondary=abstract_has_keywords)

    def __str__(self):
        return self.word_en


class Abstract(Base):
    __tablename__ = 'abstracts'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    doi = Column(String(255))
    title_en = Column(Text())
    abstract_en = Column(Text())
    title_th = Column(Text())
    abstract_th = Column(Text())
    scopus_id = Column(String(32), nullable=False, unique=True)
    authors = relationship('Author', backref=backref('abstracts'),
                        secondary=abstract_has_author)
    cited = Column(Integer())
    pub_date = Column(Date())


class Affiliation(Base):
    __tablename__ = 'affils'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    scopus_id = Column(String(64))
    name = Column(String())
    country = Column(String())
    city = Column(String())


class AffiliationHistory(Base):
    __tablename__ = 'affil_history'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    year = Column(Integer())
    affiliation_id = Column(Integer(), ForeignKey('affils.id'))
    author_id = Column(Integer(), ForeignKey('authors.id'))
    affiliation = relationship('Affiliation', backref=backref('history'))
    author = relationship('Author', backref=backref('affiliations'))


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    scopus_id = Column(String(64))
    scholarship_info_id = Column(Integer(), ForeignKey('scholarship_info.id'))
    scholarship_info = relationship("ScholarshipInfo",
                            backref=backref('author'), uselist=False)


class ScholarshipInfo(Base):
    __tablename__ = 'scholarship_info'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    first_name_en = Column(String(255))
    last_name_en = Column(String(255))
    first_name_th = Column(String(255))
    last_name_th = Column(String(255))
    country = Column(String())
    status = Column(Boolean())
    field_of_study = Column(String())
    specialty = Column(String())
    degree =Column(Integer())
    contact = Column(String())


if __name__ == '__main__':
    Base.metadata.create_all(kw_engine)