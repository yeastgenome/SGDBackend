from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.locus import Locus
from src.sgd.model.nex.literatureannotation import Literatureannotation
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.reference import Reference

__author__ = 'sweng66'

class ArchLiteratureannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'arch_literatureannotation'

    id = Column('archive_id', Integer, primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
    bud_id = Column('bud_id', Integer)
    topic = Column('topic', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_archived = Column('date_archived', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    locus = relationship(Locus, uselist=False, foreign_keys=[locus_id])
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])

    __eq_values__ = ['id', 'topic', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('locus', Locus, False),
                  ('reference', Reference, False),
                  ('taxonomy', Taxonomy, False)]

    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['locus_id', 'reference_id', 'topic']

    def __init__(self, obj_json, session):
        self.reference_id = obj_json['reference_id']
        self.taxonomy_id = obj_json['taxonomy_id']
        self.locus_id = obj_json.get('locus_id')
        UpdateWithJsonMixin.__init__(self, obj_json, session)

