from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Reftype(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'reftype'

    id = Column('reftype_id', String, primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    name = Column('name', String)
    link = Column('obj_url', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    references = association_proxy('reference_reftypes', 'reference')

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'created_by', 'date_created']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id', 'name']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        obj_json['references'] = [x.to_json(size='small', perspective='reftype') for x in self.references]
        return obj_json
