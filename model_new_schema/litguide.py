'''
Created on Jul 8, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
class Bioentevidence(Evidence):
    __tablename__ = "bioentevidence" 
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    topic = Column('topic', String)
    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    bioent_name_with_link = Column('bioent_name_with_link', String)
    type = 'BIOENT_EVIDENCE'  
    
    #Relationships 
    bioentity = relationship(Bioentity, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': "BIOENT_EVIDENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, evidence_id, reference_id, reference_name_with_link, reference_citation, topic,
                bioent_id, bioent_name_with_link, date_created, created_by):
        Evidence.__init__(self, evidence_id, None, None,
                          reference_id, reference_name_with_link, reference_citation,
                          None, None,
                          'SGD', 'BIOENT_EVIDENCE', date_created, created_by)
        self.topic = topic
        self.bioent_id = bioent_id
        self.bioent_name_with_link = bioent_name_with_link