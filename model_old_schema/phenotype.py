'''
Created on Feb 4, 2013

@author: kpaskov
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from model_old_schema.feature import Feature
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date
   
class Phenotype_Feature(Base, EqualityByIDMixin):
    __tablename__ = 'pheno_annotation'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('pheno_annotation_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    phenotype_id = Column('phenotype_no', Integer, ForeignKey('bud.phenotype.phenotype_no'))
    experiment_id = Column('experiment_no', Integer, ForeignKey('bud.experiment.experiment_no'))
    
    feature = relationship(Feature, uselist=False)

    phenotype = relationship('Phenotype', lazy='joined', uselist=False)
    source = association_proxy('phenotype', 'source')
    experiment_type = association_proxy('phenotype', 'experiment_type')
    mutant_type = association_proxy('phenotype', 'mutant_type')
    qualifier = association_proxy('phenotype', 'qualifier')
    observable = association_proxy('phenotype', 'observable')
    created_by = association_proxy('phenotype', 'created_by')
    date_created = association_proxy('phenotype', 'date_created')

    experiment = relationship('Experiment', lazy='joined', uselist=False)
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
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('expt_property_no', Integer, primary_key = True)
    type = Column('property_type', String)
    value = Column('property_value', String)
    description = Column('property_description', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
class Experiment(Base, EqualityByIDMixin):
    __tablename__ = 'experiment'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('experiment_no', Integer, primary_key = True)
    experiment_comment = Column('experiment_comment', String)
    
    properties = relationship(ExperimentProperty, secondary= Table('expt_exptprop', Base.metadata, 
                                                        Column('expt_property_no', Integer, ForeignKey('bud.expt_property.expt_property_no')),
                                                        Column('experiment_no', Integer, ForeignKey('bud.experiment.experiment_no')),
                                                        schema=SCHEMA), lazy='joined')

    