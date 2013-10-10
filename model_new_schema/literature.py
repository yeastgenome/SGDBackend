'''
Created on Jul 8, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String


class Literatureevidence(Evidence):
    __tablename__ = "literatureevidence" 
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    topic = Column('topic', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    
    #Relationships 
    bioentity = relationship(Bioentity, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': "LITERATURE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, evidence_id, reference_id, bioentity_id, topic,
                            date_created, created_by):
        Evidence.__init__(self, evidence_id, 'LITERATURE', None, reference_id, None, 'SGD', None,
                          date_created, created_by)
        self.bioentity_id = bioentity_id
        self.topic = topic
        
