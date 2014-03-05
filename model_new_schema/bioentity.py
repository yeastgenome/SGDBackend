'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base, EqualityByIDMixin, create_format_name
from model_new_schema.bioconcept import Go
from model_new_schema.misc import Alias, Url, Relation
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Numeric

class Bioentity(Base, EqualityByIDMixin):
    __tablename__ = 'bioentity'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String)
    sgdid = Column('sgdid', String)
    uniprotid = Column('uniprotid', String)
    bioent_status = Column('bioent_status', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    __mapper_args__ = {'polymorphic_on': class_type}
    
    def __init__(self, bioentity_id, display_name, format_name, class_type, link, source, sgdid, uniprotid, bioent_status, description,
                 date_created, created_by):
        self.id = bioentity_id
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.sgdid = sgdid
        self.uniprotid = uniprotid
        self.bioent_status = bioent_status
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
            
    def unique_key(self):
        return (self.format_name, self.class_type)
    
class Bioentityurl(Url):
    __tablename__ = 'bioentityurl'
    
    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    subclass_type = Column('subclass', String)
    
    bioentity = relationship(Bioentity, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Url.id}
    
    def __init__(self, display_name, link, source, category, bioentity, date_created, created_by):
        Url.__init__(self, display_name, bioentity.format_name, 'BIOENTITY', link, source, category, 
                     date_created, created_by)
        self.bioentity_id = bioentity.id
        self.subclass_type = bioentity.class_type
    
class Bioentityalias(Alias):
    __tablename__ = 'bioentityalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    subclass_type = Column('subclass', String)
    
    bioentity = relationship(Bioentity, uselist=False, backref='aliases')

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, bioentity, date_created, created_by):
        Alias.__init__(self, display_name, bioentity.format_name, 'BIOENTITY', source, category, date_created, created_by)
        self.bioentity_id = bioentity.id
        self.subclass_type = bioentity.class_type

class Bioentityrelation(Relation):
    __tablename__ = 'bioentityrelation'

    id = Column('relation_id', Integer, ForeignKey(Relation.id), primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioentity.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioentity.id))
    subclass_type = Column('subclass', String)
    
    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Relation.id}
   
    #Relationships
    parent = relationship(Bioentity, uselist=False, primaryjoin="Bioentityrelation.parent_id==Bioentity.id")
    child = relationship(Bioentity, uselist=False, primaryjoin="Bioentityrelation.child_id==Bioentity.id")

    def __init__(self, source, relation_type, parent, child, date_created, created_by):
        Relation.__init__(self, parent.format_name + '|' + child.format_name, 
                          child.display_name + ' ' + ('' if relation_type is None else relation_type + ' ') + parent.display_name, 
                          'BIOENTITY', source, relation_type, date_created, created_by)
        self.parent_id = parent.id
        self.child_id = child.id
        self.subclass_type = parent.class_type
                       
class Locus(Bioentity):
    __tablename__ = "locusbioentity"
    
    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    genetic_position = Column('genetic_position', String)
    locus_type = Column('locus_type', String)
        
    __mapper_args__ = {'polymorphic_identity': 'LOCUS',
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, bioentity_id, display_name, format_name, source, sgdid, uniprotid, bioent_status, 
                 locus_type, short_description, headline, description, genetic_position,
                 date_created, created_by):
        Bioentity.__init__(self, bioentity_id, display_name, format_name, 'LOCUS', '/cgi-bin/locus.fpl?locus=' + sgdid,
                           source, sgdid, uniprotid, bioent_status, description, date_created, created_by)
        self.short_description = short_description
        self.headline = headline
        self.genetic_position = genetic_position
        self.locus_type = locus_type
    
class Protein(Bioentity):
    __tablename__ = "proteinbioentity"

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))

    __mapper_args__ = {'polymorphic_identity': 'PROTEIN',
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, bioentity_id, source,
                 locus, date_created, created_by):
        Bioentity.__init__(self, bioentity_id, locus.display_name + 'p', locus.format_name + 'P', 
                           'PROTEIN', '/locus/' + locus.sgdid + '/overview', source, None, None, locus.bioent_status, locus.description, date_created, created_by)
        self.locus_id = locus.id

class Transcript(Bioentity):
    __tablename__ = "transcriptbioentity"

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))

    __mapper_args__ = {'polymorphic_identity': 'TRANSCRIPT',
                       'inherit_condition': id == Bioentity.id}

    def __init__(self, bioentity_id, source,
                 locus, date_created, created_by):
        Bioentity.__init__(self, bioentity_id, locus.display_name + 't', locus.format_name + 'T',
                           'TRANSCRIPT', '/locus/' + locus.sgdid + '/overview', source, None, None, locus.bioent_status, locus.description, date_created, created_by)
        self.locus_id = locus.id

class Complex(Bioentity):
    __tablename__ = 'complexbioentity'

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key = True)
    go_id = Column('go_id', Integer, ForeignKey(Go.id))
    cellular_localization = Column('cellular_localization', String)

    __mapper_args__ = {'polymorphic_identity': "COMPLEX",
                       'inherit_condition': id==Bioentity.id}

    def __init__(self, source, sgdid,
                 go, cellular_localization):
        format_name = create_format_name(go.display_name.lower())
        Bioentity.__init__(self, None, go.display_name, format_name, 'COMPLEX', '/complex/' + format_name + '/overview', source, sgdid, None, None, go.description, None, None)
        self.go_id = go.id
        self.cellular_localization = cellular_localization
