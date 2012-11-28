'''
Created on Nov 27, 2012

@author: kpaskov
'''
from model_new_schema import Base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
  
class Biorelation(Base):
    __tablename__ = "biorel"
    
    id = Column('biorel_id', Integer, primary_key = True)
    biorelation_type = Column('biorel_type', String)
    bioent1_id = Column('bioent1_id', Integer, ForeignKey('bioent.bioent_id'))
    bioent2_id = Column('bioent2_id', Integer, ForeignKey('bioent.bioent_id'))
    
    bioent1 = relationship('Bioentity', uselist=False, primaryjoin="Biorelation.bioent1_id==Bioentity.id")
    bioent2 = relationship('Bioentity', uselist=False, primaryjoin="Biorelation.bioent2_id==Bioentity.id")

    
    __mapper_args__ = {'polymorphic_on': biorelation_type,
                       'polymorphic_identity':"BIORELATION"}
    
    def __init__(self, bioent1, bioent2):
        self.bioent1 = bioent1
        self.bioent2 = bioent2
    
    def __repr__(self):
        data = self.id, self.biorelation_type, self.bioent1, self.bioent2
        return 'Biorelation(id=%s, bioentity_type=%s, bioent1=%s, bioent2=%s)' % data
    
class Interaction(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "INTERACTION"}
    
    def __init__(self, bioent1, bioent2):
        self.bioent1 = bioent1
        self.bioent2 = bioent2
    
    def __repr__(self):
        data = self.id, self.bioent1_id, self.bioent2_id
        return 'Interaction(id=%s, bioent1_id=%s, bioent2_id=%s)' % data
    
class Regulation(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "REGULATION"}
    
    def __init__(self, bioent1, bioent2):
        self.bioent1 = bioent1
        self.bioent2 = bioent2
    
    def __repr__(self):
        data = self.id, self.bioent1_id, self.bioent2_id
        return 'Regulation(id=%s, bioent1_id=%s, bioent2_id=%s)' % data
    
class Homology(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "HOMOLOGY"}
    
    def __init__(self, bioent1, bioent2):
        self.bioent1 = bioent1
        self.bioent2 = bioent2
    
    def __repr__(self):
        data = self.id, self.bioent1_id, self.bioent2_id
        return 'Homology(id=%s, bioent1_id=%s, bioent2_id=%s)' % data
    
class Structural(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "STRUCTURAL"}
    
    def __init__(self, bioent1, bioent2):
        self.bioent1 = bioent1
        self.bioent2 = bioent2
    
    def __repr__(self):
        data = self.id, self.bioent1_id, self.bioent2_id
        return 'Structural(id=%s, bioent1_id=%s, bioent2_id=%s)' % data
    
class ProteinBiosynthesis(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "PROTEIN_BIOSYNTHESIS"}
    
    def __init__(self, bioent1, bioent2):
        self.bioent1 = bioent1
        self.bioent2 = bioent2
    
    def __repr__(self):
        data = self.id, self.bioent1_id, self.bioent2_id
        return 'ProteinBiosynthesis(id=%s, bioent1_id=%s, bioent2_id=%s)' % data
