from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Dbentity(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'dbentity'

    id = Column('dbentity_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    sgdid = Column('sgdid', String)
    bud_id = Column('bud_id', Integer)
    dbentity_status = Column('dbentity_status', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'sgdid', 
                     'class_type', 'dbentity_status', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __mapper_args__ = {'polymorphic_on': class_type}
    __id_values__ = ['sgdid', 'format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['dbentity_status']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.format_name, self.class_type

    @classmethod
    def __create_display_name__(cls, obj_json):
        return obj_json['sgdid'] if 'display_name' not in obj_json else obj_json['display_name']

    @classmethod
    def __create_link__(cls, obj_json):
        return '/' + cls.__name__.lower() + '/' + obj_json['sgdid']

