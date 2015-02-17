from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Book(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'book'

    id = Column('book_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', String)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'bud_id', 'link', 'title', 'volume_title', 'isbn', 'total_pages',
                     'publisher', 'publisher_location',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']
    __id_values__ = ['format_name', 'id']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.display_name = self.title
        self.format_name = create_format_name(self.title + '' if self.volume_title is None else ('_' + self.volume_title))
        self.link = '/book/' + self.format_name

    def unique_key(self):
        return self.title, self.volume_title