'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base, plural_to_singular, subclasses
from model_new_schema.bioconcept import Bioconcept, bioent_biocon_map
from model_new_schema.biorelation import Biorelation
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
    
class Bioentity(Base):
    __tablename__ = "bioent"
    
    id = Column('bioent_id', Integer, primary_key = True)
    name = Column('name', String)
    type = Column('bioent_type', String)
    
    __mapper_args__ = {'polymorphic_on': type,
                       'polymorphic_identity':"BIOENTITY"}
    
    biorel_source = relationship(Biorelation, primaryjoin="Biorelation.sink_bioent_id==Bioentity.id")
    biorel_sink = relationship(Biorelation, primaryjoin="Biorelation.source_bioent_id==Bioentity.id")
    
    bioconcepts = relationship(Bioconcept, secondary=bioent_biocon_map, backref='bioentities')
    
    @hybrid_property
    def biorelations(self):
        return self.biorel_source + self.biorel_sink
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.name
        return '%s(id=%s, name=%s)' % data
    
    def __getattr__(self, name):
        singular_name = plural_to_singular(name).upper()
        if singular_name in subclasses(Biorelation):
            return filter(lambda x: x.type == singular_name, self.biorelations)
        elif singular_name in subclasses(Bioconcept):
            return filter(lambda x: x.type == singular_name, self.bioconcepts)
        raise AttributeError() 

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
    
class Intron(Bioentity):
    __mapper_args__ = {'polymorphic_identity': "INTRON"}
    
class CDS(Bioentity):
    __mapper_args__ = {'polymorphic_identity': "CDS"}

    
