'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.misc import Alias, Url
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

class Bioentity(Base, EqualityByIDMixin):
    __tablename__ = 'bioentity'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String)
    sgdid = Column('sgdid', String)
    bioent_status = Column('bioent_status', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    __mapper_args__ = {'polymorphic_on': class_type}
    
    def __init__(self, bioentity_id, display_name, format_name, class_type, link, source, sgdid, bioent_status,
                 date_created, created_by):
        self.id = bioentity_id
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.sgdid = sgdid
        self.bioent_status = bioent_status
        self.date_created = date_created
        self.created_by = created_by
            
    def unique_key(self):
        return (self.format_name, self.class_type)
    
class Bioentityurl(Url):
    __tablename__ = 'bioentityurl'
    
    url_id = Column('url_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    
    bioentity = relationship(Bioentity, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Url.id}
    
    def __init__(self, display_name, link, source, category, bioentity, date_created, created_by):
        Url.__init__(self, display_name, bioentity.format_name, 'BIOENTITY', link, source, category, 
                     bioentity.id, date_created, created_by)
        self.bioentity_id = bioentity.id
    
class Bioentityalias(Alias):
    __tablename__ = 'bioentityalias'
    
    alias_id = Column('alias_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    
    bioentity = relationship(Bioentity, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, bioentity, date_created, created_by):
        Alias.__init__(self, display_name, bioentity.format_name, 'BIOENTITY', source, category, date_created, created_by)
        self.bioentity_id = bioentity.id
    
                       
class Locus(Bioentity):
    __tablename__ = "locusbioentity"
    
    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    description = Column('description', String)
    genetic_position = Column('genetic_position', String)
    locus_type = Column('locus_type', String)
        
    __mapper_args__ = {'polymorphic_identity': 'LOCUS',
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, bioentity_id, display_name, format_name, source, sgdid, bioent_status, 
                 locus_type, short_description, headline, description, genetic_position,
                 date_created, created_by):
        Bioentity.__init__(self, bioentity_id, display_name, format_name, 'LOCUS', 'http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=' + format_name,
                           source, sgdid, bioent_status, date_created, created_by)
        self.short_description = short_description
        self.headline = headline
        self.description = description
        self.genetic_position = genetic_position
        self.locus_type = locus_type
    
class Protein(Bioentity):
    __tablename__ = "proteinbioentity"
    
    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
    molecular_weight = Column('molecular_weight', Integer)
    length = Column('protein_length', Integer)
    n_term_seq = Column('n_term_seq', String)
    c_term_seq = Column('c_term_seq', String)
            
    __mapper_args__ = {'polymorphic_identity': 'PROTEIN',
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, bioentity_id, source,
                 locus, length, n_term_seq, c_term_seq,
                 date_created, created_by):
        Bioentity.__init__(self, bioentity_id, locus.display_name + 'p', locus.format_name + 'P', 
                           'PROTEIN', locus.link.replace('/locus.f', '/protein/proteinPage.'), source, None, locus.bioent_status, date_created, created_by)
        self.locus_id = locus.id
        self.length = length
        self.n_term_seq = n_term_seq
        self.c_term_seq = c_term_seq

    
