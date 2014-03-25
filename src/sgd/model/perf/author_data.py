from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base
from src.sgd.model import EqualityByIDMixin
from core import Author


__author__ = 'kpaskov'

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
