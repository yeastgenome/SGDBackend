from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Author(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'author'

    id = Column('author_id', String, primary_key = True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'bud_id',  'created_by', 'date_created']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id', 'name']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        references = sorted(set([x.reference for x in self.references]), key=lambda x: (x.year, x.date_published), reverse=True)
        obj_json['references'] = [x.to_json('medium') for x in references]
        return obj_json