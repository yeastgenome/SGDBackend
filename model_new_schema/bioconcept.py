'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin
from model_new_schema.config import SCHEMA
from model_new_schema.link_maker import add_link, link_symbol, biocon_link, \
    bioent_biocon_link, bioent_biocon_evidence_link, biocon_all_bioent_link
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
import datetime

class BioentBioconEvidence(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'bioent_biocon_evidence'

    
    id = Column('bioent_biocon_evidence_id', Integer, primary_key=True)
    bioent_biocon_id = Column('bioent_biocon_id', Integer, ForeignKey('sprout.bioent_biocon.bioent_biocon_id'))
    evidence_id = Column('evidence_id', Integer, ForeignKey('sprout.evidence.evidence_id'))
    
    bioent_biocon = relationship('BioentBiocon', uselist=False, backref=backref('bioent_biocon_evidences'))
    evidence = relationship('Evidence', uselist=False, backref=backref('bioent_biocon_evidences', uselist=False))
    
    def __init__(self, bioent_biocon_id, evidence_id):
        self.bioent_biocon_id = bioent_biocon_id
        self.evidence_id = evidence_id
    
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
    biocon_type = Column('biocon_type', String)
    official_name = Column('name', String)
    evidence_count = Column('evidence_count', Integer)
    evidence_desc = Column('evidence_desc', String)
    
    evidences = association_proxy('bioent_biocon_evidences', 'evidence')
    
    bioentity = relationship('Bioentity', uselist=False, backref='bioent_biocons')
    bioconcept = relationship('Bioconcept', uselist=False, backref='bioent_biocons')
    type = "BIOENT_BIOCON"

    
    def __init__(self, bioent_id, biocon_id, official_name, biocon_type, session=None):
        self.bioent_id = bioent_id
        self.biocon_id = biocon_id
        self.official_name = official_name
        self.biocon_type = biocon_type
        
    @hybrid_property
    def name(self):
        return self.bioentity.name + link_symbol + self.bioconcept.name
    @hybrid_property
    def name_for_biocon(self):
        return link_symbol + self.bioentity.name 
    @hybrid_property
    def name_for_bioent(self):
        return link_symbol + self.bioconcept.name
    
    @hybrid_property
    def name_with_link(self):
        return add_link(self.name, self.link)
    @hybrid_property
    def name_for_biocon_with_link(self):
        return add_link(self.name_for_biocon, self.link)
    @hybrid_property
    def name_for_bioent_with_link(self):
        return add_link(self.name_for_bioent, self.link)
    
    @hybrid_property
    def link(self):
        return bioent_biocon_link(self)
    @hybrid_property
    def evidence_link(self):
        return bioent_biocon_evidence_link(self)
    
    @hybrid_property
    def description(self):
        return 'Relationship between bioentity ' + self.bioentity.full_name + ' and bioconcept ' + self.bioconcept.name + '.'  

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
    official_name = Column('name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': biocon_type,
                       'polymorphic_identity':"BIOCONCEPT",
                       'with_polymorphic':'*'}
     
     
    @hybrid_property
    def link(self):
        return biocon_link(self)
    @hybrid_property
    def all_bioent_link(self):
        return biocon_all_bioent_link(self)
    
    @hybrid_property
    def name(self):
        return self.official_name
    
    @hybrid_property
    def name_with_link(self):
        return add_link(self.name, self.link)
    
    @hybrid_property
    def description(self):
        return self.biocon_type.lower() + ' ' + self.name
    
    @classmethod
    def unique_hash(cls, biocon_type, official_name):
        return '%s_%s' % (biocon_type, official_name) 

    @classmethod
    def unique_filter(cls, query, biocon_type, official_name):
        return query.filter(Bioconcept.biocon_type == biocon_type, Bioconcept.official_name == official_name)
        
    def __init__(self, biocon_type, official_name, session=None, biocon_id=None, date_created=None, created_by=None):
        self.biocon_type = biocon_type
        self.official_name = official_name
        
        if session is None:
            self.id=biocon_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.official_name
        return '%s(id=%s, name=%s)' % data
    
class Phenotype(Bioconcept):
    __tablename__ = "phenotype"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    observable = Column('observable', String)
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Bioconcept.id}

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
    
class Go(Bioconcept):
    __tablename__ = 'go_term'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    go_go_id = Column('go_go_id', Integer)
    go_term = Column('go_term', String)
    go_aspect = Column('go_aspect', String)
    go_definition = Column('go_definition', String)
    
    def __init__(self, go_go_id, go_term, go_aspect, go_definition, session=None, biocon_id=None, date_created=None, created_by=None):
        name = go_term
        Bioconcept.__init__(self, 'GO', name, session=session, biocon_id=biocon_id, date_created=date_created, created_by=created_by)
        self.go_go_id = go_go_id
        self.go_term = go_term
        self.go_aspect = go_aspect
        self.go_definition = go_definition
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Bioconcept.id}
    
class Function(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "FUNCTION",
                       'inherit_condition': id==Bioconcept.id}
    





    