'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
    
class Bioentity(Base):
    __tablename__ = "bioent"
    
    id = Column('bioent_id', Integer, primary_key = True)
    name = Column('name', String)
    bioentity_type = Column('bioent_type', String)
    
    __mapper_args__ = {'polymorphic_on': bioentity_type,
                       'polymorphic_identity':"BIOENTITY"}
    
    biorel_source = relationship('Biorelation', primaryjoin="Biorelation.bioent1_id==Bioentity.id")
    biorel_sink = relationship('Biorelation', primaryjoin="Biorelation.bioent2_id==Bioentity.id")
    
    @hybrid_property
    def biorelations(self):
        return self.biorel_source + self.biorel_sink
   
    @hybrid_property 
    def interactions(self):
        return filter(lambda x: x.biorelation_type == 'INTERACTION', self.biorelations)
    
    def __init__(self, name, bioentity_type):
        self.name = name
        self.bioentity_type = bioentity_type
    
    def __repr__(self):
        data = self.id, self.name, self.bioentity_type
        return 'Bioentity(id=%s, name=%s, bioentity_type=%s)' % data

class Orf(Bioentity):
    __tablename__ = "orf"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key = True)
    systematic_name = Column('sys_name', String)
    description = Column('descr', String)
    
    __mapper_args__ = {'polymorphic_identity': "ORF",
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, name, bioentity_type, systematic_name, description):
        self.name = name
        self.bioentity_type = bioentity_type
        self.systematic_name = systematic_name
        self.description = description
        
    def __repr__(self):
        data = self.id, self.name, self.systematic_name, self.description
        return 'Orf(id=%s, name=%s, systematic_name=%s, description=%s)' % data
    
class NotPhysicallyMapped(Bioentity):
    __mapper_args__ = {'polymorphic_identity': "NOT_PHYSICALLY_MAPPED"}
    
    def __init__(self, name, bioentity_type):
        self.name = name
        self.bioentity_type = bioentity_type
    
    def __repr__(self):
        data = self.id, self.name
        return 'Bioentity(id=%s, name=%s)' % data