from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Book(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'book'

    id = Column('book_id', String, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
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

    __eq_values__ = ['id', 'name', 'bud_id', 'link', 'title', 'volume_title', 'isbn', 'total_pages',
                     'publisher', 'publisher_location',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = ['volume_title', 'publisher']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.title, self.volume_title

    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['title'] = self.title
        obj_json['volume_title'] = self.volume_title
        return obj_json

    @classmethod
    def __create_name__(cls, obj_json):
        return obj_json['title']

    @classmethod
    def specialized_find(cls, obj_json, session):
        return session.query(cls).\
            filter_by(title=obj_json['title']).\
            filter_by(volume_title=None if 'volume_title' not in obj_json else obj_json['volume_title']).first()
