from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Reftype(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
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
    references = association_proxy('reference_reftypes', 'reference')

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'created_by', 'date_created']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        obj_json['reference_reftypes'] = [x.to_min_json() for x in self.references]
        return obj_json

    def to_semi_json(self):
        return self.to_min_json()
