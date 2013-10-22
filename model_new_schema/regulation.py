'''
Created on May 16, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

class Regulationevidence(Evidence):
    __tablename__ = "regulationevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Bioentity.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Bioentity.id))
       
    __mapper_args__ = {'polymorphic_identity': 'REGULATION',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, evidence_id, source, reference, strain, experiment, note, 
                 bioentity1, bioentity2, conditions,
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, bioentity1.format_name + '|' + bioentity2.format_name + '|' + reference.format_name + '|' + ','.join([condition.id for condition in conditions]), 
                          'REGULATION', source, reference, strain, experiment, note, date_created, created_by)
        self.bioentity1_id = bioentity1.id
        self.bioentity2_id = bioentity2.id
