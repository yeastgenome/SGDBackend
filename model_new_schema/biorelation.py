'''
Created on Nov 27, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin, SCHEMA
from model_new_schema.evidence import Evidence
from model_new_schema.link_maker import link_symbol, add_link, biorel_link, \
    biorel_evidence_link
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
import datetime

class Biorelation(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = "biorel"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('biorel_id', Integer, primary_key = True)
    official_name = Column('name', String)
    biorel_type = Column('biorel_type', String)
    source_bioent_id = Column('bioent_id1', Integer, ForeignKey('sprout.bioent.bioent_id'))
    sink_bioent_id = Column('bioent_id2', Integer, ForeignKey('sprout.bioent.bioent_id'))
    evidence_count = Column('evidence_count', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    type = 'BIORELATION'
    
    #Relationships
    source_bioent = relationship('Bioentity', uselist=False, primaryjoin="Biorelation.source_bioent_id==Bioentity.id", lazy='joined', backref='biorel_source')
    sink_bioent = relationship('Bioentity', uselist=False, primaryjoin="Biorelation.sink_bioent_id==Bioentity.id", lazy='joined', backref='biorel_sink')

    biorel_evidences = relationship('BiorelEvidence')
    evidences = association_proxy('biorel_evidences', 'evidence')
        
    __mapper_args__ = {'polymorphic_on': biorel_type,
                       'polymorphic_identity':"BIORELATION",
                       'with_polymorphic':'*'}
    
    @hybrid_property
    def name(self):
        return self.source_bioent.name + link_symbol + self.sink_bioent.name
    @hybrid_property
    def name_for_source(self):
        return link_symbol + self.sink_bioent.name
    @hybrid_property
    def name_for_sink(self):
        return link_symbol + self.source_bioent.name
    def get_name_for(self, bioent):
        if bioent == self.source_bioent:
            return self.name_for_source
        elif bioent == self.sink_bioent:
            return self.name_for_sink
        else:
            return None
        
    @hybrid_property
    def description(self):
        return 'Interaction between ' + self.source_bioent.full_name + ' and ' + self.sink_bioent.full_name    
    @hybrid_property
    def link(self):
        return biorel_link(self)
        
    @hybrid_property
    def name_with_link(self):
        return add_link(self.name, self.link)
    @hybrid_property
    def name_for_source_with_link(self):
        return add_link(self.name_for_source, self.link)
    @hybrid_property
    def name_for_sink_with_link(self):
        return add_link(self.name_for_sink, self.link)
    def get_name_with_link_for(self, bioent):
        return add_link(self.get_name_for(bioent), self.link)
    
    @hybrid_property
    def evidence_link(self):
        return biorel_evidence_link(self)

    @classmethod
    def unique_hash(cls, biorel_type, source_bioent_id, sink_bioent_id):
        return '%s_%s_%s' % (biorel_type, source_bioent_id, sink_bioent_id) 

    @classmethod
    def unique_filter(cls, query, biorel_type, source_bioent_id, sink_bioent_id):
        return query.filter(Biorelation.biorel_type == biorel_type, Biorelation.source_bioent_id == source_bioent_id, Biorelation.sink_bioent_id == sink_bioent_id)
    
    def __init__(self, biorel_type, source_bioent_id, sink_bioent_id, session=None, biorel_id=None, created_by=None, date_created=None):
        self.source_bioent_id = source_bioent_id
        self.sink_bioent_id = sink_bioent_id
        self.biorel_type = biorel_type
        
        if session is None:
            self.created_by = created_by
            self.date_created = date_created
            self.id = biorel_id
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.source_bioent.name, self.sink_bioent.name
        return '%s(id=%s, source_name=%s, sink_name=%s)' % data

class Interaction(Biorelation):
    __tablename__ = "interaction"

    id = Column('biorel_id', Integer, ForeignKey(Biorelation.id), primary_key = True)
    physical_evidence_count = Column('physical_evidence_count', Integer)
    genetic_evidence_count = Column('genetic_evidence_count', Integer)
        
    __mapper_args__ = {'polymorphic_identity': 'INTERACTION',
                       'inherit_condition': id == Biorelation.id}
    
class Regulation(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "REGULATION"}
    
class Homology(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "HOMOLOGY"}
    
class Structural(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "STRUCTURAL"}

class ProteinBiosynthesis(Biorelation):
    __mapper_args__ = {'polymorphic_identity': "PROTEIN_BIOSYNTHESIS"}
    
class BiorelEvidence(Base, UniqueMixin):
    __tablename__ = "biorel_evidence"
    biorel_evidence_id = Column('biorel_evidence_id', Integer, primary_key=True)
    biorel_id = Column('biorel_id', Integer, ForeignKey('sprout.biorel.biorel_id'))
    evidence_id = Column('evidence_id', Integer, ForeignKey('sprout.evidence.evidence_id'))

    #Relationships
    evidence = relationship(Evidence, backref=backref('biorel_evidence', uselist=False))
    biorel = relationship(Biorelation, uselist=False)

