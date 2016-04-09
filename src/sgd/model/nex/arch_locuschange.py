from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.locus import Locus

__author__ = 'sweng66'

class ArchLocuschange(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'arch_locuschange'

    id = Column('archive_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Locus.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    change_type = Column('change_type', String)
    old_value = Column('old_value', String)
    new_value = Column('new_value', String)
    date_changed = Column('date_changed', Date, server_default=FetchedValue())
    changed_by = Column('changed_by', String, server_default=FetchedValue())
    date_archived = Column('date_archived', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    
    __eq_values__ = ['id', 'dbentity_id', 'bud_id', 'change_type', 'old_value', 'new_value', 'date_changed', 
                     'changed_by', 'date_archived']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_changed', 'changed_by', 'date_archived']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

