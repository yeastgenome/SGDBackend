'''
Created on Nov 27, 2012

@author: kpaskov
'''
from model_new_schema import Base, CommonEqualityMixin
from model_new_schema.evidence import Evidence, biorel_evidence_map
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
  
class Biorelation(Base, CommonEqualityMixin):
    __tablename__ = "biorel"
    
    id = Column('biorel_id', Integer, primary_key = True)
    type = Column('biorel_type', String)
    source_bioent_id = Column('bioent_id1', Integer, ForeignKey('bioent.bioent_id'))
    sink_bioent_id = Column('bioent_id2', Integer, ForeignKey('bioent.bioent_id'))
    
    source_bioent = relationship('Bioentity', uselist=False, primaryjoin="Biorelation.source_bioent_id==Bioentity.id")
    sink_bioent = relationship('Bioentity', uselist=False, primaryjoin="Biorelation.sink_bioent_id==Bioentity.id")
    
    evidences = relationship(Evidence, secondary=biorel_evidence_map)

    __mapper_args__ = {'polymorphic_on': type,
                       'polymorphic_identity':"BIORELATION"}
    
    def __init__(self, source_bioent, sink_bioent):
        self.source_bioent = source_bioent
        self.sink_bioent = sink_bioent
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.source_bioent.name, self.sink_bioent.name
        return '%s(id=%s, source_name=%s, sink_name=%s)' % data
        
class Interaction(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "INTERACTION"}
    
class Regulation(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "REGULATION"}
    
class Homology(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "HOMOLOGY"}
    
class Structural(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "STRUCTURAL"}
    
class ProteinBiosynthesis(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "PROTEIN_BIOSYNTHESIS"}
