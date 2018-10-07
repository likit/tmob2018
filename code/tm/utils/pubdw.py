from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, Table, Column, Text, Date,
                        Integer, String, ForeignKey, Boolean)
from sqlalchemy.orm import Session, relationship, backref

Base = declarative_base()


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
    author_list_id = Column(Integer, ForeignKey('author_lists.id'))


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


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    scopus_id = Column(String(64))
    pub_lists = relationship('AuthorList', backref='author')


class AuthorList(Base):
    __tablename__ = 'author_lists'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
