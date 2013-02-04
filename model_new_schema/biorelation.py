'''
Created on Nov 27, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin, SCHEMA
from model_new_schema.evidence import Evidence
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date
import datetime

class Biorelation(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = "biorel"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('biorel_id', Integer, primary_key = True)
    biorel_type = Column('biorel_type', String)
    source_bioent_id = Column('bioent_id1', Integer, ForeignKey('sprout.bioent.bioent_id'))
    sink_bioent_id = Column('bioent_id2', Integer, ForeignKey('sprout.bioent.bioent_id'))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    #source_bioent = relationship('Bioentity', uselist=False, primaryjoin="Biorelation.source_bioent_id==Bioentity.id")
    #sink_bioent = relationship('Bioentity', uselist=False, primaryjoin="Biorelation.sink_bioent_id==Bioentity.id")
        
    evidences = relationship(Evidence, secondary= Table('sprout.biorel_evidence', Base.metadata,
                                                        Column('biorel_id', Integer, ForeignKey('sprout.biorel.biorel_id')),
                                                        Column('evidence_id', Integer, ForeignKey('sprout.evidence.evidence_id'))))
    
    __mapper_args__ = {'polymorphic_on': biorel_type,
                       'polymorphic_identity':"BIORELATION"}
    
    @classmethod
    def unique_hash(cls, biorel_type, source_bioent_id, sink_bioent_id):
        return '%s_%s_%s' % (biorel_type, source_bioent_id, sink_bioent_id) 

    @classmethod
    def unique_filter(cls, query, biorel_type, source_bioent_id, sink_bioent_id):
        return query.filter(Biorelation.biorel_type == biorel_type, Biorelation.source_bioent_id == source_bioent_id, Biorelation.sink_bioent_id == sink_bioent_id)
    
    def __init__(self, session, source_bioent, sink_bioent):
        self.source_bioent = source_bioent
        self.sink_bioent = sink_bioent
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
    
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


