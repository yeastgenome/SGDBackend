'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, plural_to_singular, subclasses
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String
  

class Bioconcept(Base):
    __tablename__ = "biocon"
    
    id = Column('biocon_id', Integer, primary_key = True)
    type = Column('biocon_type', String)
    name = Column('name', String)
    
    __mapper_args__ = {'polymorphic_on': type,
                       'polymorphic_identity':"BIOCONCEPT"}
    
    def __init__(self, source_bioent, sink_bioent):
        self.source_bioent = source_bioent
        self.sink_bioent = sink_bioent
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.name
        return '%s(id=%s, name=%s)' % data
    
    def __getattr__(self, name):
        singular_name = plural_to_singular(name).upper()
        from bioentity_declarative import Bioentity
        if singular_name in subclasses(Bioentity):
            return filter(lambda x: x.type == singular_name, self.bioentities)
        raise AttributeError() 
    
class Metagene(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "METAGENE"}
    
class Strain(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "STRAIN"}
    
class GOTerm(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "GO_TERM"}
    
class Phenotype(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE"}
    
class Function(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "FUNCTION"}

bioent_biocon_map = Table('bioent_biocon', Base.metadata,
    Column('bioent_id', Integer, ForeignKey('bioent.bioent_id')),
    Column('biocon_id', Integer, ForeignKey('biocon.biocon_id'))
)
    