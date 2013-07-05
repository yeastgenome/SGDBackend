'''
Created on Mar 4, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.link_maker import add_link
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Allele(Base):
    __tablename__ = 'allele'
    id = Column('allele_id', Integer, primary_key=True)
    official_name = Column('name', String)
    more_info = Column('description', String)
    
    def unique_key(self):
        return self.official_name
    
    @hybrid_property
    def name(self):
        return self.official_name
    
    @hybrid_property
    def description(self):
        return 'Allele'
    
    def __init__(self, name, description):
        self.official_name = name
        self.more_info = description
        
class Url(Base):
    __tablename__ = 'url'
    id = Column('url_id', Integer, primary_key=True)
    url = Column('url', String)
    display_name = Column('display_name', String)
    category = Column('category', String)
    source = Column('source', String)
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': url_type,
                       'polymorphic_identity':"URL"}
    
    def __init__(self, url, display_name, category, url_type, source, date_created, created_by):
        self.url = url
        self.display_name = display_name
        self.category = category
        self.url_type = url_type
        self.source = source
        self.date_created = date_created
        self.created_by = created_by
        
    @hybrid_property
    def name_with_link(self):
        return add_link(self.display_name, self.url, new_window=True) 
    
class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'
    
    id = Column('alias_id', Integer, primary_key=True)
    name = Column('name', String)
    alias_type = Column('alias_type', String)
    source = Column('source', String)
    used_for_search = Column('used_for_search', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': alias_type,
                       'polymorphic_identity':"ALIAS"}
        
    def __init__(self, name, alias_type, source, used_for_search, date_created, created_by):
        self.name = name
        self.alias_type = alias_type
        self.source = source
        self.used_for_search = used_for_search
        self.date_created = date_created
        self.created_by = created_by
        
class Altid(Base, EqualityByIDMixin):
    __tablename__ = 'altid'
    
    id = Column('altid_id', Integer, primary_key=True)
    identifier = Column('identifier', String)
    source = Column('source', String)
    altid_type = Column('altid_type', String)
    altid_name = Column('altid_name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': altid_type,
                       'polymorphic_identity':"ALTID"}
        
    def __init__(self, identifier, altid_type, source, altid_name, date_created, created_by):
        self.identifier = identifier
        self.altid_type = altid_type
        self.source = source
        self.altid_name = altid_name
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.identifier, self.altid_type, self.altid_name)
    
class Note(Base, EqualityByIDMixin):
    __tablename__ = 'note'
    
    id = Column('note_id', Integer, primary_key=True)
    note = Column('note', String)
    note_type = Column('note_type', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': note_type,
                       'polymorphic_identity':"NOTE"}
        
    def __init__(self, note, note_type, date_created, created_by):
        self.note = note
        self.note_type = note_type
        self.date_created = date_created
        self.created_by = created_by
       
        
        
        
    
    
    