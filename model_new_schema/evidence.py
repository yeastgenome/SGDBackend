'''
Created on Dec 11, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.reference import Reference
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Evidence(Base, EqualityByIDMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    experiment_type = Column('experiment_type', String)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    evidence_type = Column('evidence_type', String)
    strain_id = Column('strain_id', String)
    source = Column('source', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': evidence_type,
                       'polymorphic_identity':"EVIDENCE",
                       'with_polymorphic':'*'}
    
    #Relationships
    reference = relationship('Reference', backref='evidences', uselist=False)
    
    def __init__(self, evidence_id, experiment_type, reference_id, evidence_type, strain_id, date_created, created_by):
        self.id = evidence_id
        self.experiment_type = experiment_type
        self.reference_id = reference_id
        self.evidence_type = evidence_type
        self.strain_id = strain_id
        self.date_created = date_created
        self.created_by = created_by
    
    def __repr__(self):
        data = self.__class__.__name__, self.id
        return '%s(id=%s)' % data
    

        

    
    

        
        

        

          
        