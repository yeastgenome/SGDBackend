from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean, CLOB
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateWithJsonMixin, ToJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.ro import Ro
from src.sgd.model.nex.locus import Locus

__author__ = 'sweng66'

class LocusRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'locus_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    parent_id = Column('parent_id', Integer, ForeignKey(Locus.id, ondelete='CASCADE'))
    child_id = Column('child_id', Integer, ForeignKey(Locus.id, ondelete='CASCADE'))
    ro_id = Column('ro_id', Integer, ForeignKey(Ro.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    source = relationship(Source, uselist=False)
    ro = relationship(Ro, uselist=False)

    __eq_values__ = ['id', 'ro_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('ro', Ro, False)]

    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.parent_id = obj_json['parent_id']
        self.child_id = obj_json['child_id']
        self.bud_id = obj_json['bud_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.parent_id, self.child_id, self.ro_id

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        return obj_json

        

