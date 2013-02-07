'''
Created on Feb 6, 2013

@author: kpaskov
'''
from model_old_schema import Base, EqualityByIDMixin
from model_old_schema.phenotype import Phenotype
from model_old_schema.reference import Reference
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
import datetime

class Interaction(Base, EqualityByIDMixin):
    __tablename__ = 'interaction'

    id = Column('interaction_no', Integer, primary_key = True)
    interaction_type = Column('interaction_type', String)
    experiment_type = Column('experiment_type', String)
    annotation_type = Column('annotation_type', String)
    source = Column('source', String)
    modification = Column('modification', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    interaction_reference = relationship('Interaction_Reference', lazy='subquery')
    notes = association_proxy('interaction_reference', 'note')
    references = association_proxy('interaction_reference', 'reference')
    
    interaction_phenotype = relationship('Interaction_Phenotype', lazy='subquery')
    qualifiers = association_proxy('interaction_phenotype', 'qualifier')
    observables = association_proxy('interaction_phenotype', 'observable')
    
    feature_interactions = relationship('Interaction_Feature', collection_class=attribute_mapped_collection('action'), lazy='joined')
    features = association_proxy('feature_interactions', 'feature')
    
    def __init__(self, session, interaction_type, experiment_type, annotation_type, source, modification):
        self.interaction_type = interaction_type
        self.experiment_type = experiment_type
        self.annotation_type = annotation_type
        self.source = source
        self.modification = modification
        
        self.created_by = session.user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.experiment_type
        return 'Interaction(experiment_type=%s)' % data
    
class Interaction_Reference(Base, EqualityByIDMixin):
    __tablename__ = 'interact_ref'

    id = Column('interact_ref_no', Integer, primary_key=True)
    interaction_id = Column('interaction_no', Integer, ForeignKey('bud.interaction.interaction_no'))
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    note = Column('note', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    
    #Relationships
    reference = relationship('Reference', uselist=False, lazy='subquery')
    
class Interaction_Phenotype(Base, EqualityByIDMixin):
    __tablename__ = 'interact_pheno'

    id = Column('interact_pheno_no', Integer, primary_key=True)
    interaction_id = Column('interaction_no', Integer, ForeignKey('bud.interaction.interaction_no'))
    phenotype_id = Column('phenotype_no', Integer, ForeignKey('bud.phenotype.phenotype_no'))
    
    #Relationships
    phenotype = relationship(Phenotype, uselist=False, lazy='subquery')
    qualifier = association_proxy('phenotype', 'qualifier')
    observable = association_proxy('phenotype', 'observable')
    
class Interaction_Feature(Base, EqualityByIDMixin):
    __tablename__ = 'feat_interact'
    
    id = Column('feat_interact_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    interaction_id = Column('interaction_no', Integer, ForeignKey('bud.interaction.interaction_no'))
    action = Column('action', String)
        
    feature = relationship('Feature', lazy='subquery') 