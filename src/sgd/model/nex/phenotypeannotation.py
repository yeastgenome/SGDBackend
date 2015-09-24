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
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
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
    analysis_id = Column('analysis_id', Integer, ForeignKey(Obi.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    locus = relationship(Locus, uselist=False)
    reference = relationship(Reference, uselist=False)
    phenotype = relationship(Phenotype, uselist=False)
    experiment = relationship(Apo, uselist=False)
    mutant = relationship(Apo, uselist=False)
    allele = relationship(Allele, uselist=False)
    reporter = relationship(Reporter, uselist=False)
    
    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('locus', Locus, False),
                  ('reference', Reference, False),
                  ('phenoDetails', phenotypeannotation.PhenotypeDetail, True)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['locus_id', 'reference_id', 'phenotype_id']

    def __init__(self, obj_json, session):
        # self.qualifier_id = obj_json.get('qualifier_id')
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['locus'] = self.locus.display_name
        obj_json['phenotype'] = self.phenotype.display_name
        obj_json['experiment'] = self.experiment.display_name
        obj_json['mutant'] = self.mutant.display_name
        return obj_json

    def __to_medium_json__(self):
        obj_json = ToJsonMixin.__to_medium_json__(self)
        obj_json['locus'] = self.locus.display_name
        obj_json['phenotype'] = self.phenotype.display_name
        obj_json['experiment'] = self.experiment.display_name
        obj_json['mutant'] = self.mutant.display_name
        obj_json['reference'] = self.reference.citation
        return obj_json

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        obj_json['locus'] = self.locus.display_name
        obj_json['phenotype'] = self.phenotype.display_name
        obj_json['experiment'] = self.experiment.display_name
        obj_json['mutant'] = self.mutant.display_name
        obj_json['reference'] = self.reference.citation
        obj_json['allele'] = self.allele.display_name
        obj_json['reporter'] = self.reporter.display_name
        obj_json['phenoDetailss'] = [x.to_json() for x in self.phenoDetails]
        return obj_json


class PhenotypeDetail(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'phenotypeannotation_detail'

    id = Column('detail_id', Integer, primary_key=True)
    annotation_id = Column('annotation_id', Integer, ForeignKey(Phenotypeannotation.id, ondelete='CASCADE'))
    detail_type = Column('detail_type', String)
    detail_name = Column('detail_name', String)
    detail_value = Column('detail_value', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    annotation = relationship(Phenotypeannotation, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))

    __eq_values__ = ['id', 'detail_type', 'detail_name', 'detail_value', 'detail_type', 'date_created', 'created_by']
    __eq_fks__ = []
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.annotation is None else self.annotation.unique_key()), self.detail_type, self.detail_name, self.detail_value

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.annotation_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(annotation_id=newly_created_object.annotation_id)\
            .filter_by(detail_type=newly_created_object.detail_type)\
            .filter_by(detail_name=newly_created_object.detail_name)\
            .filter_by(detail_value=newly_created_object.detail_value).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'detail_type': self.detail_type,
            'detail_name': self.detail_name,
            'detail_value': self.detail_value
        }

 

