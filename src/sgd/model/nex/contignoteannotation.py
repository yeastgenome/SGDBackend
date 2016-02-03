from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.contig import Contig
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.reference import Reference

__author__ = 'sweng66'

class Contignoteannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'contignoteannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    contig_id = Column('contig_id', Integer, ForeignKey(Contig.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    bud_id = Column('bud_id', Integer)
    note_type = Column('note_type', String)
    display_name = Column('display_name', String)
    note = Column('note', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    contig = relationship(Contig, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    reference = relationship(Reference, uselist=False)

    __eq_values__ = ['id', 'contig_id', 'taxonomy_id', 'reference_id', 'bud_id', 'note_type', 'display_name', 'note', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)




