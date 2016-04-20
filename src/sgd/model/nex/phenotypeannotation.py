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
from src.sgd.model.nex.phenotype import Phenotype
from src.sgd.model.nex.allele import Allele
from src.sgd.model.nex.reporter import Reporter
from src.sgd.model.nex.chebi import Chebi
from src.sgd.model.nex.obi import Obi

__author__ = 'sweng66'

class Phenotypeannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'phenotypeannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Locus.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    phenotype_id = Column('phenotype_id', Integer, ForeignKey(Phenotype.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Apo.id))
    mutant_id = Column('mutant_id', Integer, ForeignKey(Apo.id))
    allele_id = Column('allele_id', Integer, ForeignKey(Allele.id))
    reporter_id = Column('reporter_id', Integer, ForeignKey(Reporter.id))
    assay_id = Column('assay_id', Integer, ForeignKey(Obi.id))
    strain_name = Column('strain_name', String)
    details = Column('details', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    locus = relationship(Locus, uselist=False)
    reference = relationship(Reference, uselist=False)
    phenotype = relationship(Phenotype, uselist=False)
    # experiment = relationship(Apo, uselist=False)
    # mutant = relationship(Apo, uselist=False)
    allele = relationship(Allele, uselist=False)
    reporter = relationship(Reporter, uselist=False)
    assay = relationship(Obi, uselist=False)

    __eq_values__ = ['id', 'dbentity_id', 'taxonomy_id', 'reference_id', 'phenotype_id', 'experiment_id', 'mutant_id', 'allele_id', 'reporter_id',  'assay_id', 'strain_name', 'details', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('locus', Locus, False),
                  ('reference', Reference, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['locus_id', 'reference_id', 'phenotype_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)



