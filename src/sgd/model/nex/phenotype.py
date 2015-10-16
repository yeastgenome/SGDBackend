from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.apo import Apo

__author__ = 'kelley, sweng66'

class Phenotype(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'phenotype'

    id = Column('phenotype_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    observable_id = Column('observable_id', ForeignKey(Apo.id))
    qualifier_id = Column('qualifier_id', Integer)
    # qualifier_id = Column('qualifier_id', ForeignKey(Apo.id))
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    # observable = relationship(Observable, uselist=False)
    # qualifier = relationship(Qualifier, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    #              ('observable', Observable, False),
    #              ('qualifier', Qualifier, False)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['observable_id', 'qualifier_id']

    def __init__(self, obj_json, session):
        self.observable_id = obj_json['observable_id']
        self.qualifier_id = obj_json.get('qualifier_id')
        self.link = obj_json.get('link')
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_format_name__(cls, obj_json):
        return create_format_name(('' if 'qualifier' not in obj_json else obj_json['qualifier'] + '.') + obj_json['observable'])[:100]  

    @classmethod
    def __create_display_name__(cls, obj_json):
        return (obj_json['observable'] + ('' if 'qualifier' not in obj_json else ': ' + obj_json['qualifier']))[:500] 


