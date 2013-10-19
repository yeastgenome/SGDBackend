'''
Created on May 16, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Regulationevidence(Evidence):
    __tablename__ = "regulationevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Bioentity.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Bioentity.id))
    conditions = Column('conditions', String)
       
    __mapper_args__ = {'polymorphic_identity': 'REGULATION',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, evidence_id, experiment_id, reference_id, strain_id, source_id, 
                 bioentity1_id, bioentity2_id, conditions,
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, 'REGULATION', 
                          experiment_id, reference_id, strain_id, source_id, None,
                          date_created, created_by)
        self.bioentity1_id = bioentity1_id
        self.bioentity2_id = bioentity2_id
        self.conditions = conditions
