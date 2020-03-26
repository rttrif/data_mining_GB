import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.orm import relationship

Base = declarative_base()

as_tag_post = Table('tag_post', Base.metadata,
                    Column('post', Integer, ForeignKey('post.id')),
                    Column('tag', Integer, ForeignKey('tag.id'))
                    )


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    date = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    writer_id = Column(Integer, ForeignKey('user.id'))
    writer = relationship('User', back_populates="post")
    comment = relationship('Comment', back_populates="post")
    tags = relationship('Tag', secondary=as_tag_post, backref='post')

    def __init__(self, title, url, writer, date):
        self.title = title
        self.url = url
        self.writer = writer
        self.date = date


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    writer_id = Column(Integer, ForeignKey('user.id'))
    writer = relationship('User', back_populates="comment")
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship('Post', back_populates="comment")

    def __init__(self, writer, post):
        self.writer = writer
        self.post = post


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', back_populates="writer")
    comment = relationship('Comment', back_populates="writer")

    def __init__(self, name, url):
        self.name = name
        self.url = url


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)

    def __init__(self, name, url):
        self.name = name
        self.url = url
