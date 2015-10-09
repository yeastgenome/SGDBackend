from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.locus import Locus
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.reference import Reference

__author__ = 'sweng66'

class Literatureannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'literatureannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    topic = Column('topic', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    locus = relationship(Locus, uselist=False)
    reference = relationship(Reference, uselist=False)
        
    __eq_values__ = ['id', 'topic', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('locus', Locus, False),
                  ('reference', Reference, False),
                  ('taxonomy', Taxonomy, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['locus_id', 'reference_id']

    def __init__(self, obj_json, session):
        self.locus_id = obj_json['locus_id']
        self.reference_id = obj_json['reference_id']
        self.taxonomy_id = obj_json['taxonomy_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['locus'] = self.locus.display_name
        obj_json['reference'] = self.phenotype.citation
        return obj_json

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        obj_json['locus'] = self.locus.display_name
        obj_json['reference'] = self.reference.citation
        obj_json['topic'] = self.topic
        return obj_json

 

