__author__ = 'kpaskov'

import datetime
from src.sgd.model import EqualityByIDMixin
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model.nex import create_format_name, Base, UpdateByJsonMixin


class Source(EqualityByIDMixin, UpdateByJsonMixin, Base):
    __tablename__ = 'source'

    id = Column('id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by']
    __min_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type', 'description']
    __fks__ = ['urls', 'aliases', 'relations', 'qualities', 'annotations', 'tags']
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)


class BasicObject(EqualityByIDMixin, UpdateByJsonMixin, Base):
    __tablename__ = 'basicobject'

    id = Column('id', Integer, primary_key=True)
    class_type = Column('class', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    tags = association_proxy('tag_basicobjects', 'tag')
    references = association_proxy('reference_basicobjects', 'reference')

    __mapper_args__ = {'polymorphic_on': class_type}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type']
    __min_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type', 'description']
    __fks__ = ['source']
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)




