from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, CLOB, Numeric
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.arch_contig import ArchContig
from src.sgd.model.nex.genomerelease import Genomerelease

__author__ = 'sweng66'

class ArchContigchange(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'arch_contigchange'

    id = Column('archive_id', Integer, primary_key=True)
    contig_id = Column('contig_id', Integer, ForeignKey(ArchContig.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    genomerelease_id = Column('genomerelease_id', Integer, ForeignKey(Genomerelease.id))
    change_type = Column('change_type', String)
    change_min_coord = Column('change_min_coord', Integer)
    change_max_coord = Column('change_max_coord', Integer)
    old_value = Column('old_value', String)
    new_value = Column('new_value', String)
    date_changed = Column('date_changed', Date, server_default=FetchedValue())
    changed_by = Column('changed_by', String, server_default=FetchedValue())
    date_archived = Column('date_archived', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    genomerelease = relationship(Genomerelease, uselist=False)
    
    __eq_values__ = ['id', 'bud_id', 'contig_id', 'genomerelease_id', 'change_type', 'change_min_coord', 
                     'change_max_coord', 'old_value', 'new_value', 'date_changed', 'changed_by', 
                     'date_archived']
    __eq_fks__ = [('source', Source, False),
                  ('genomerelease', Genomerelease, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_changed', 'changed_by']
    __filter_values__ = ['genomerelease_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

