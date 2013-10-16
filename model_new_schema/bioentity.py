'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.evidence import Evidence
from model_new_schema.misc import Alias, Url
from model_new_schema.reference import Reference
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB

class Bioentity(Base, EqualityByIDMixin):
    __tablename__ = 'bioentity'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    dbxref = Column('dbxref', String)
    link = Column('obj_link', String)
    class_type = Column('class', String)
    source = Column('source', String)
    status = Column('status', String)
    
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': class_type}
    
    #Relationships
    aliases = association_proxy('bioentityaliases', 'display_name')
            
    def __init__(self, bioentity_id, class_type, display_name, format_name, dbxref, link, source, status,
                 date_created, created_by):
        self.id = bioentity_id
        self.class_type = class_type
        self.display_name = display_name
        self.format_name = format_name
        self.dbxref = dbxref
        self.link = link
        self.source = source
        self.status = status
        self.date_created = date_created
        self.created_by = created_by
            
    def unique_key(self):
        return (self.format_name, self.class_type)
    
    @hybrid_property
    def alias_str(self):
        return ', '.join(self.aliases)
    
    
class Bioentityalias(Alias):
    __tablename__ = 'bioentityalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    
    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Alias.id}
        
    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('bioentityaliases', passive_deletes=True))
        
    def __init__(self, display_name, source, category, bioentity_id, date_created, created_by):
        Alias.__init__(self, 'BIOENTITY', display_name, source, category, date_created, created_by)
        self.bioentity_id = bioentity_id
        
    def unique_key(self):
        return (self.display_name, self.bioentity_id)
    
class Bioentityurl(Url):
    __tablename__ = 'bioentityurl'
    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    bioentity_id = Column('bioentity_id', ForeignKey(Bioentity.id))
    
    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Url.id}
    
    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('urls', passive_deletes=True))
    
    def __init__(self, display_name, source, url, category, bioentity_id, date_created, created_by):
        Url.__init__(self, 'BIOENTITY', display_name, source, url, category, date_created, created_by)
        self.bioentity_id = bioentity_id
        
    def unique_key(self):
        return (self.url, self.category, self.bioentity_id)
                       
class Locus(Bioentity):
    __tablename__ = "locusbioentity"
    
    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    attribute = Column('attribute', String)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    description = Column('description', String)
    genetic_position = Column('genetic_position', String)
    locus_type = Column('locus_type', String)
        
    __mapper_args__ = {'polymorphic_identity': 'LOCUS',
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, bioentity_id, display_name, format_name, dbxref, link, source, status, 
                 locus_type, attribute, short_description, headline, description, genetic_position,
                 date_created, created_by):
        Bioentity.__init__(self, bioentity_id, 'LOCUS',  display_name, format_name, dbxref, link, source, status, date_created, created_by)
        self.locus_type = locus_type
        self.dbxref = dbxref
        self.attribute = attribute
        self.short_description = short_description
        self.headline = headline
        self.description = description
        self.genetic_position = genetic_position
        
class Generalbioentity(Bioentity, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id==Bioentity.id} 
    
class Protein(Bioentity):
    __tablename__ = "proteinbioentity"
    
    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Bioentity.id))
    molecular_weight = Column('molecular_weight', Integer)
    length = Column('protein_length', Integer)
    n_term_seq = Column('n_term_seq', String)
    c_term_seq = Column('c_term_seq', String)
        
    __mapper_args__ = {'polymorphic_identity': 'PROTEIN',
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, bioentity_id, display_name, format_name, dbxref, link,
                 locus_id, length, n_term_seq, c_term_seq,
                 date_created, created_by):
        Bioentity.__init__(self, bioentity_id, 'PROTEIN',  display_name, format_name, dbxref, link, 'SGD', None, date_created, created_by)
        self.locus_id = locus_id
        self.length = length
        self.n_term_seq = n_term_seq
        self.c_term_seq = c_term_seq
        
class Qualifierevidence(Evidence):
    __tablename__ = "qualifierevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    qualifier = Column('qualifier', String)
    
    __mapper_args__ = {'polymorphic_identity': 'QUALIFIER',
                       'inherit_condition': id == Evidence.id}
    
    def __init__(self, evidence_id, strain_id, bioentity_id, qualifier,
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, 'QUALIFIER', None, None, strain_id, 'SGD', None, date_created, created_by)
        self.bioentity_id = bioentity_id
        self.qualifier = qualifier
    
class Paragraph(Base, EqualityByIDMixin):
    __tablename__ = 'paragraph'
    
    id = Column('paragraph_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    class_type = Column('class', String)
    text = Column('text', CLOB)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    references = association_proxy('paragraph_references', 'reference')
        
    def __init__(self, bioentity_id, class_type, text, date_created, created_by):
        self.bioentity_id = bioentity_id
        self.class_type = class_type
        self.text = text
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.class_type, self.bioentity_id)
    
class ParagraphReference(Base, EqualityByIDMixin):
    __tablename__ = 'paragraph_reference'
    
    id = Column('paragraph_reference_id', Integer, primary_key=True)
    paragraph_id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    class_type = Column('class', String)
    
    #Relationships
    paragraph = relationship(Paragraph, uselist=False, backref='paragraph_references')
    reference = relationship(Reference, uselist=False)
        
    def __init__(self, paragraph_id, reference_id, class_type):
        self.paragraph_id = paragraph_id
        self.reference_id = reference_id
        self.class_type = class_type
        
    def unique_key(self):
        return (self.paragraph_id, self.reference_id)
    
