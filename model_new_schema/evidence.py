'''
Created on Dec 11, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.chemical import Chemical
from model_new_schema.evelement import Experiment, Strain
from model_new_schema.reference import Reference
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Evidence(Base, EqualityByIDMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    evidence_type = Column('evidence_type', String)
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    source = Column('source', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    reference = relationship(Reference, backref=backref('evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, uselist=False)
    strain = relationship(Strain, uselist=False)
    chemicals = association_proxy('ev_chemicals', 'chemical')
    
    __mapper_args__ = {'polymorphic_on': evidence_type,
                       'polymorphic_identity':"EVIDENCE"}
    
    
    def __init__(self, evidence_id, experiment_id, reference_id, evidence_type, strain_id, source, date_created, created_by):
        self.id = evidence_id
        self.experiment_id = experiment_id
        self.reference_id = reference_id
        self.evidence_type = evidence_type
        self.strain_id = strain_id
        self.source = source
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.id
    
class EvidenceChemical(Base, EqualityByIDMixin):
    __tablename__ = 'evidence_chemical'
    
    id = Column('evidence_chemical_id', Integer, primary_key=True)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    chemical_amt = Column('chemical_amount', String)
    
    #Relationships
    chemical = relationship(Chemical, uselist=False, lazy='joined')
    evidence = relationship(Evidence, backref=backref('ev_chemicals', passive_deletes=True), uselist=False)
    chemical_name = association_proxy('chemical', 'display_name')
    
    def __init__(self, evidence_id, chemical_id, chemical_amt):
        self.evidence_id = evidence_id
        self.chemical_id = chemical_id
        self.chemical_amt = chemical_amt
    
    def unique_key(self):
        return (self.evidence_id, self.chemical_id)

    
        

    
    

        
        

        

          
        