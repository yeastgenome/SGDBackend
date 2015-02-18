from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Reftype(Base, EqualityByIDMixin, ToJsonMixin):
    __tablename__ = 'reftype'

    id = Column('reftype_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'created_by', 'date_created']
    __eq_fks__ = ['source']
    __id_values__ = ['format_name', 'id']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = create_format_name(self.display_name)
        self.link = '/reftype/' + self.format_name

    def unique_key(self):
        return self.format_name
