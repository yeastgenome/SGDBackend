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
from src.sgd.model.nex.go import Go
from src.sgd.model.nex.eco import Eco

__author__ = 'sweng66'

class Goannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'goannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    go_id = Column('go_id', Integer, ForeignKey(Go.id))
    eco_id = Column('eco_id', Integer, ForeignKey(Eco.id))
    annotation_type = Column('annotation_type', String)
    go_qualifier = Column('go_qualifier', String)
    date_assigned = Column('date_assigned', Date, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    locus = relationship(Locus, uselist=False)
    reference = relationship(Reference, uselist=False)
    go = relationship(Go, uselist=False)
    eco = relationship(Eco, uselist=False)

    __eq_values__ = ['id', 'annotation_type', 'bud_id', 'date_assigned', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('locus', Locus, False),
                  ('reference', Reference, False),
                  ('taxonomy', Taxonomy, False),
                  ('go', Go, False),
                  ('eco', Eco, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['locus_id', 'reference_id', 'go_id']

    def __init__(self, obj_json, session):
        self.locus_id = obj_json['locus_id']
        self.reference_id = obj_json['reference_id']
        self.taxonomy_id = obj_json['taxonomy_id']
        self.go_id = obj_json['go_id']
        self.eco_id = obj_json['eco_id']
        self.go_qualifier = obj_json['go_qualifier']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['locus'] = self.locus.display_name
        obj_json['reference'] = self.phenotype.citation
        obj_json['go'] = self.go.display_name
        obj_json['annotation_type'] = self.annotation_type
        return obj_json

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        obj_json['locus'] = self.locus.display_name
        obj_json['reference'] = self.phenotype.citation
        obj_json['go'] = self.go.display_name
        obj_json['annotation_type'] = self.annotation_type
        obj_json['eco'] = self.eco.display_name
        obj_json['date_assigned'] = self.date_assigned
        return obj_json

 

