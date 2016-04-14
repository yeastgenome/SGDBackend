from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.apo import Apo
from src.sgd.model.nex.locus import Locus
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.obi import Obi

__author__ = 'sweng66'

class Proteinexptannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'proteinexptannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    locus_id = Column('dbentity_id', Integer, ForeignKey(Locus.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    experiment_type = Column('experiment_type', String)
    data_value = Column('data_value', String)
    data_unit = Column('data_unit', String)
    assay_id = Column('assay_id', Integer, ForeignKey(Obi.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    locus = relationship(Locus, uselist=False)
    reference = relationship(Reference, uselist=False)

    __eq_values__ = ['id', 'locus_id', 'taxonomy_id', 'reference_id', 'experiment_type', 'data_value', 'data_unit', 'assay_id', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('locus', Locus, False),
                  ('taxonomy', Taxonomy, False),
                  ('reference', Reference, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['locus_id', 'reference_id', 'experiment_type']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)


