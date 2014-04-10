from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base
from phenotype import Phenotype
from reference import Reference


__author__ = 'kpaskov'

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
    interaction_references = relationship('Interaction_Reference')
    reference_ids = association_proxy('interaction_references', 'reference_id')
    
    feature_ids = association_proxy('interaction_features', 'feature_id')

    def __repr__(self):
        data = self.experiment_type
        return 'Interaction(experiment_type=%s)' % data
    
class Interaction_Reference(Base, EqualityByIDMixin):
    __tablename__ = 'interact_ref'

    id = Column('interact_ref_no', Integer, primary_key=True)
    interaction_id = Column('interaction_no', Integer, ForeignKey('from_bud.interaction.interaction_no'))
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    note = Column('note', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    reference = relationship('Reference', uselist=False, lazy='subquery')
    
class Interaction_Phenotype(Base, EqualityByIDMixin):
    __tablename__ = 'interact_pheno'

    id = Column('interact_pheno_no', Integer, primary_key=True)
    interaction_id = Column('interaction_no', Integer, ForeignKey('from_bud.interaction.interaction_no'))
    phenotype_id = Column('phenotype_no', Integer, ForeignKey('from_bud.phenotype.phenotype_no'))
    
    #Relationships
    phenotype = relationship(Phenotype, uselist=False)
    interaction = relationship(Interaction, uselist=False, backref='interaction_phenotypes')
    qualifier = association_proxy('phenotype', 'qualifier')
    observable = association_proxy('phenotype', 'observable')
    mutant_type = association_proxy('phenotype', 'mutant_type')
    
class Interaction_Feature(Base, EqualityByIDMixin):
    __tablename__ = 'feat_interact'
    
    id = Column('feat_interact_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey('from_bud.feature.feature_no'))
    interaction_id = Column('interaction_no', Integer, ForeignKey('from_bud.interaction.interaction_no'))
    action = Column('action', String)
        
    feature = relationship('Feature', uselist=False) 
    interaction = relationship(Interaction, backref='interaction_features', uselist=False)
