'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin
from model_new_schema.config import SCHEMA
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
import datetime

class BioentBioconEvidence(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'bioent_biocon_evidence'

    
    id = Column('bioent_biocon_evidence_id', Integer, primary_key=True)
    bioent_biocon_id = Column('bioent_biocon_id', Integer, ForeignKey('sprout.bioent_biocon.bioent_biocon_id'))
    evidence_id = Column('evidence_id', Integer, ForeignKey('sprout.evidence.evidence_id'))
    
    bioent_biocon = relationship('BioentBiocon', uselist=False)
    evidence = relationship('Evidence', uselist=False, backref=backref('bioent_biocon_evidence', uselist=False))
        
    @classmethod
    def unique_hash(cls, bioent_biocon_id, evidence_id):
        return '%s_%s' % (bioent_biocon_id, evidence_id) 

    @classmethod
    def unique_filter(cls, query, bioent_biocon_evidence, evidence_id):
        return query.filter(BioentBioconEvidence.bioent_biocon_evidence == bioent_biocon_evidence, BioentBioconEvidence.evidence_id == evidence_id)
    
class BioentBiocon(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'bioent_biocon'

    id = Column('bioent_biocon_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey('sprout.bioent.bioent_id'))
    biocon_id = Column('biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    name = Column('name', String)
    evidence_count = Column('evidence_count', Integer)
    evidence_desc = Column('evidence_desc', String)
    
    bioent_biocon_evidences = relationship(BioentBioconEvidence)
    evidences = association_proxy('bioent_biocon_evidences', 'evidence')
    
    bioentity = relationship('Bioentity', uselist=False)
    bioconcept = relationship('Bioconcept', uselist=False)
    
    def __init__(self, bioent, biocon_id, session=None):
        self.bioentity = bioent
        self.biocon_id = biocon_id
        
    @classmethod
    def unique_hash(cls, bioent_id, biocon_id):
        return '%s_%s' % (bioent_id, biocon_id) 

    @classmethod
    def unique_filter(cls, query, bioent_id, biocon_id):
        return query.filter(BioentBiocon.bioent_id == bioent_id, BioentBiocon.biocon_id == biocon_id)
    

          
class Bioconcept(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = "biocon"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
        
    id = Column('biocon_id', Integer, primary_key = True)
    biocon_type = Column('biocon_type', String)
    name = Column('name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': biocon_type,
                       'polymorphic_identity':"BIOCONCEPT"}
 
    bioent_biocons = relationship(BioentBiocon)
    
    @hybrid_property
    def bioentities(self):
        return self.bioentity_evidence.keys()
    
    @classmethod
    def unique_hash(cls, biocon_type, name):
        return '%s_%s' % (biocon_type, name) 

    @classmethod
    def unique_filter(cls, query, biocon_type, name):
        return query.filter(Bioconcept.biocon_type == biocon_type, Bioconcept.name == name)
        
    def __init__(self, biocon_type, name, session=None, biocon_id=None, date_created=None, created_by=None):
        self.biocon_type = biocon_type
        self.name = name
        
        if session is None:
            self.id=biocon_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.name
        return '%s(id=%s, name=%s)' % data
    
class Phenotype(Bioconcept):
    __tablename__ = "phenotype"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    observable = Column('observable', String)
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE"}

    def __init__(self, observable, session=None, biocon_id=None, date_created=None, created_by=None):
        name = observable
        Bioconcept.__init__(self, 'PHENOTYPE', name, session=session, biocon_id=biocon_id, date_created=date_created, created_by=created_by)
        self.observable = str(observable)
         
        
    @classmethod
    def unique_hash(cls, qualifier, observable):
        return '%s_%s' % (qualifier, observable) 

    @classmethod
    def unique_filter(cls, query, qualifier, observable):
        return query.filter(Phenotype.qualifier == qualifier, Phenotype.observable == observable)
    
    
    
class Chemical(Bioconcept):
    __tablename__ = "chemical"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    name = Column('name', String)
    description = Column('description', String)
      
    __mapper_args__ = {'polymorphic_identity': "CHEMICAL"}

    def __init__(self, name, description, session=None, biocon_id=None, date_created=None, created_by=None):
        Bioconcept.__init__(self, 'CHEMICAL', name, session=session, biocon_id=biocon_id, date_created=date_created, created_by=created_by)
        self.description = description
        
    @classmethod
    def unique_hash(cls, name):
        return '%s_%s' % (name) 

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(Chemical.name == name)

class GOTerm(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "GO_TERM"}
    
class Function(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "FUNCTION"}
    





    