'''
Created on Oct 21, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Qualifierevidence(Evidence):
    __tablename__ = "qualifierevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    qualifier = Column('qualifier', String)
    
    bioentity = relationship(Bioentity, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': 'QUALIFIER',
                       'inherit_condition': id == Evidence.id}
    
    def __init__(self, evidence_id, strain, source, bioentity, qualifier,
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, bioentity.format_name + '|' + strain.format_name, 
                          'QUALIFIER', source, None, strain, None, None, date_created, created_by)
        self.bioentity_id = bioentity.id
        self.qualifier = qualifier