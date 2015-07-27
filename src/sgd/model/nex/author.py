from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Author(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'author'

    id = Column('author_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id',  'created_by', 'date_created']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        references = set([x.reference for x in self.reference_authors])
        obj_json['references'] = [x.to_semi_json() for x in sorted(references, key=lambda x: (x.year, x.date_published), reverse=True)]
        return obj_json
