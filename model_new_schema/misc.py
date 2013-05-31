'''
Created on Mar 4, 2013

@author: kpaskov
'''
from model_new_schema import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Chemical(Base):
    __tablename__ = "chemical"
    
    id = Column('chemical_id', Integer, primary_key=True)
    name = Column('name', String)
    
    def __init__(self, name):
        self.name = name
        
    def unique_key(self):
        return self.name

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
    source = Column('source', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    def __init__(self, url_id, url, source, date_created, created_by):
        self.id = url_id
        self.url = url
        self.source = source
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.url
        
class ExternalObject(Base):
    __tablename__ = 'externalobj'
    id = Column('externalobj_id', Integer, primary_key=True)
    name = Column('name', String)
    source = Column('source', String)
    external_id = Column('external_id', String)
    url_id = Column('primary_url_id', Integer)#, ForeignKey(Url))
    assoc_bioent_id = Column('assoc_bioent_id', Integer, ForeignKey('bioent.bioent_id'))
    assoc_biocon_id = Column('assoc_biocon_id', Integer, ForeignKey('biocon.biocon_id'))
    
    #relationships
    #url = relationship(Url)
    
    def __init__(self, external_obj_id, name, source, external_id, assoc_bioent_id, assoc_biocon_id):
        self.id = external_obj_id
        self.name = name
        self.source = source
        self.external_id = external_id
        self.assoc_bioent_id = assoc_bioent_id
        self.assoc_biocon_id = assoc_biocon_id
        
    def unique_key(self):
        return (self.name, self.source)
        
        
        
    
    
    