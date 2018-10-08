from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, Table, Column, Text, Date,
                        Integer, String, ForeignKey, Boolean)
from sqlalchemy.orm import Session, relationship, backref

Base = declarative_base()


class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    word_en = Column(String(64), nullable=False, index=True)
    word_th = Column(String(64), nullable=False, index=True)
    abstract_id = Column(Integer(), ForeignKey('abstracts.id'))
    count = Column(Integer())
    word_lists = relationship('KeywordList', backref='keyword')
    noun_chunk_word_lists = relationship('NounChunkWordList', backref='keyword')

    def __str__(self):
        return self.word_en


class NounChunk(Base):
    __tablename__ = 'noun_chunks'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    chunk_en = Column(String(255), nullable=False)
    chunk_th = Column(String(255), nullable=False)
    is_auth_keywords = Column(Boolean(), default=False)
    keywords = relationship('NounChunkWordList', backref='noun_chunk')
    nounchunk_lists = relationship('NounChunkList', backref='noun_chunk')


class KeywordList(Base):
    __tablename__ = 'keyword_lists'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'))
    field_pub_id = Column(Integer, ForeignKey('field_pubs.id'))


class NounChunkWordList(Base):
    __tablename__ = 'noun_chunk_word_lists'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'))
    noun_chunk_id = Column(Integer, ForeignKey('noun_chunks.id'))


class NounChunkList(Base):
    __tablename__ = 'noun_chunk_lists'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    noun_chunk_id = Column(Integer, ForeignKey('noun_chunks.id'))
    field_pub_id = Column(Integer, ForeignKey('field_pubs.id'))


class Field(Base):
    __tablename__ = 'fields'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    abbr = Column(String(8))
    fullname = Column(String(64))
    scopus_id = Column(String(16))
    pubs = relationship('FieldPub', backref='field')


class FieldPub(Base):
    __tablename__ = 'field_pubs'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    field_id  = Column(Integer, ForeignKey('fields.id'))
    abstract_id = Column(Integer, ForeignKey('abstracts.id'))
    authors = relationship('AuthorList', backref='field_pub')
    keywords = relationship('KeywordList', backref='field_pub')
    nounchunks = relationship('NounChunkList', backref='field_pub')


class Abstract(Base):
    __tablename__ = 'abstracts'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    doi = Column(String(255))
    title_en = Column(Text())
    abstract_en = Column(Text())
    title_th = Column(Text())
    abstract_th = Column(Text())
    scopus_id = Column(String(32), nullable=False, unique=True)
    cited = Column(Integer())
    pub_date = Column(Date())
    fields = relationship('FieldPub', backref='abstract')
    words = relationship('Keyword', backref='abstract')


class Affiliation(Base):
    __tablename__ = 'affils'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    scopus_id = Column(String(64))
    name = Column(String())
    country = Column(String())
    city = Column(String())
    pub_lists = relationship('AuthorList', backref='affil')


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    scopus_id = Column(String(64))
    pub_lists = relationship('AuthorList', backref='author')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class AuthorList(Base):
    __tablename__ = 'author_lists'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    affil_id = Column(Integer, ForeignKey('affils.id'))
    field_pub_id = Column(Integer, ForeignKey('field_pubs.id'))
