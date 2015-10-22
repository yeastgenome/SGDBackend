from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.go import Go


__author__ = 'sweng66'

class Goslim(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'goslim'

    id = Column('goslim_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    go_id = Column('go_id', Integer, ForeignKey(Go.id))
    slim_name = Column('slim_name', String)
    genome_count = Column('genome_count', Integer)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    go = relationship(Go, uselist=False)

    __eq_values__ = ['id', 'format_name', 'display_name', 'bud_id', 'go_id', 'slim_name', 'genome_count', 
                     'link', 'description', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('go', Go, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['format_name', 'slim_name', 'go_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['slim_name'] = self.slim_name
        obj_json['display_name'] = self.display_name
        obj_json['go'] = self.go.display_name
        return obj_json

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        obj_json['slim_name'] = self.slim_name
        obj_json['go'] = self.go.display_name
        obj_json['display_name'] = self.display_name
        obj_json['genome_count'] = self.genome_count
        obj_json['description'] = self.description
        return obj_json

 
