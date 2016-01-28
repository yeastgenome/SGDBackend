from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.locus import Locus
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.reference import Reference

__author__ = 'sweng66'

class Bindingmotifannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'bindingmotifannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Locus.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    bud_id = Column('bud_id', Integer)
    link = Column('obj_url', String)
    motif_id = Column('motif_id', Integer)
    logo_url = Column('logo_url', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    locus = relationship(Locus, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    reference = relationship(Reference, uselist=False)

    __eq_values__ = ['id', 'dbentity_id', 'taxonomy_id', 'reference_id', 'bud_id', 'link', 'motif_id', 'logo_url', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id', 'motif_id']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)




