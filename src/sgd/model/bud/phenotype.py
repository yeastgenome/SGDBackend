from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base


__author__ = 'kpaskov'

class PhenotypeFeature(Base, EqualityByIDMixin):
    __tablename__ = 'pheno_annotation'

    id = Column('pheno_annotation_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    phenotype_id = Column('phenotype_no', Integer, ForeignKey('bud.phenotype.phenotype_no'))
    experiment_id = Column('experiment_no', Integer, ForeignKey('bud.experiment.experiment_no'))
    
    phenotype = relationship('Phenotype', uselist=False, backref='phenotype_features')
    source = association_proxy('phenotype', 'source')
    experiment_type = association_proxy('phenotype', 'experiment_type')
    mutant_type = association_proxy('phenotype', 'mutant_type')
    qualifier = association_proxy('phenotype', 'qualifier')
    observable = association_proxy('phenotype', 'observable')
    created_by = association_proxy('phenotype', 'created_by')
    date_created = association_proxy('phenotype', 'date_created')

    experiment = relationship('Experiment', uselist=False, backref='phenotypefeature')
    experiment_comment = association_proxy('experiment', 'experiment_comment')
    experiment_properties = association_proxy('experiment', 'properties')
     
class Phenotype(Base, EqualityByIDMixin):
    __tablename__ = 'phenotype'

    id = Column('phenotype_no', Integer, primary_key=True)
    source = Column('source', String)
    experiment_type = Column('experiment_type', String)
    mutant_type = Column('mutant_type', String)
    qualifier = Column('qualifier', String)
    observable = Column('observable', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
class ExperimentProperty(Base, EqualityByIDMixin):
    __tablename__ = 'expt_property'

    id = Column('expt_property_no', Integer, primary_key = True)
    type = Column('property_type', String)
    value = Column('property_value', String)
    description = Column('property_description', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
class Experiment(Base, EqualityByIDMixin):
    __tablename__ = 'experiment'

    id = Column('experiment_no', Integer, primary_key = True)
    experiment_comment = Column('experiment_comment', String)

    properties = association_proxy('experiment_experimentproperties', 'experiment_property')
    
    @hybrid_property
    def chemicals(self):
        chemicals = []
        for prop in self.properties:
            if prop.type == 'Chemical_pending' or prop.type == 'chebi_ontology':
                chemicals.append((prop.value, prop.description))
        return chemicals
    
    @hybrid_property
    def allele(self):
        for prop in self.properties:
            if prop.type == 'Allele':
                return (prop.value, prop.description)
        return None
    
    @hybrid_property
    def reporter(self):
        for prop in self.properties:
            if prop.type == 'Reporter':
                return (prop.value, prop.description)
        return None
    
    @hybrid_property
    def strain(self):
        for prop in self.properties:
            if prop.type == 'strain_background':
                return (prop.value, prop.description)
        return None
    
    @hybrid_property
    def budding_index(self):
        for prop in self.properties:
            if prop.type == 'Numerical_value' and prop.description == 'relative budding index compared to control':
                return prop.value
        return None    
    
    @hybrid_property
    def glutathione_excretion(self):
        for prop in self.properties:
            if prop.type == 'Numerical_value' and prop.description == 'Fold elevation of glutathione excretion':
                return prop.value
        return None  
    
    @hybrid_property
    def z_score(self):
        for prop in self.properties:
            if prop.type == 'Numerical_value' and prop.description == 'Fitness defect score (Z-score)':
                return prop.value
        return None  
    
    @hybrid_property
    def relative_fitness_score(self):
        for prop in self.properties:
            if prop.type == 'Numerical_value' and prop.description == 'Relative fitness score':
                return prop.value
        return None  
    
    @hybrid_property
    def chitin_level(self):
        for prop in self.properties:
            if prop.type == 'Numerical_value' and prop.description == 'Chitin level (nmole GlcNAc/mg dry weight)':
                return prop.value
        return None  
    
    @hybrid_property
    def condition(self):
        return_value = []
        for prop in self.properties:
            if prop.type == 'Condition':
                return_value.append((prop.value, prop.description))
        return return_value
    
    @hybrid_property
    def details(self):
        return_value = []
        for prop in self.properties:
            if prop.type == 'Details':
                return_value.append((prop.value, prop.description))
        return return_value

class Experiment_ExperimentProp(Base, EqualityByIDMixin):
    __tablename__ = 'expt_exptprop'

    id = Column('expt_exptprop_no', Integer, primary_key = True)
    experiment_property_id = Column('expt_property_no', Integer, ForeignKey(ExperimentProperty.id))
    experiment_id = Column('experiment_no', Integer, ForeignKey(Experiment.id))

    experiment_property = relationship(ExperimentProperty, uselist=False, backref='experiment_experimentproperties')
    experiment = relationship(Experiment, uselist=False, backref='experiment_experimentproperties')