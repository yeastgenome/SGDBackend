from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Dbentity(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'dbentity'

    id = Column('dbentity_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    sgdid = Column('sgdid', String)
    uniprotid = Column('uniprotid', String)
    bud_id = Column('bud_id', Integer)
    dbent_status = Column('dbent_status', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description',
                     'bud_id', 'date_created', 'created_by', 'sgdid', 'uniprotid', 'dbent_status']
    __eq_fks__ = ['source']
    __mapper_args__ = {'polymorphic_on': class_type}

    def unique_key(self):
        return self.format_name, self.class_type

