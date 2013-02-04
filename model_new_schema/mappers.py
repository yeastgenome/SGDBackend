'''
Created on Feb 1, 2013

@author: kpaskov
'''
from model_new_schema import Base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer

class BioentBiocon(Base):
    __tablename__ = 'bioent_biocon'

    bioent_biocon_id = Column('bioent_biocon_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey('sprout.bioent.bioent_id'))
    biocon_id = Column('biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    
    evidences = relationship('Evidence', secondary= Table('sprout.bioent_biocon_evidence', Base.metadata,
                                                        Column('bioent_biocon_id', Integer, ForeignKey('sprout.bioent_biocon.bioent_biocon_id')),
                                                        Column('evidence_id', Integer, ForeignKey('sprout.evidence.evidence_id'))))
