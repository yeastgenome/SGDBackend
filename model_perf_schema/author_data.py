'''
Created on Oct 28, 2013

@author: kpaskov
'''
from model_perf_schema import EqualityByIDMixin, Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String
from core import Author

class AuthorDetails(Base, EqualityByIDMixin):
    __tablename__ = 'author_details'

    id = Column('author_details_id', Integer, primary_key=True)
    author_id = Column('author_id', Integer, ForeignKey(Author.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, author_id, class_type, json):
        self.author_id = author_id
        self.class_type = class_type
        self.json = json
