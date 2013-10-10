'''
Created on Mar 4, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Date

class Allele(Base):
    __tablename__ = 'allele'
    id = Column('allele_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_link', String)
    description = Column('description', String)
    
    def unique_key(self):
        return self.format_name
    
    def __init__(self, display_name, format_name, link, description):
        self.display_name = display_name
        self.format_name = format_name
        self.link = link
        self.description = description
        
class Url(Base):
    __tablename__ = 'url'
    id = Column('url_id', Integer, primary_key=True)
    class_type = Column('class', String)
    url = Column('url', String)
    display_name = Column('display_name', String)
    category = Column('category', String)
    source = Column('source', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"URL"}
    
    def __init__(self, class_type, display_name, source, url, category, date_created, created_by):
        self.class_type = class_type
        self.display_name = display_name
        self.source = source
        self.url = url
        self.category = category
        self.date_created = date_created
        self.created_by = created_by
    
class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'
    
    id = Column('alias_id', Integer, primary_key=True)
    class_type = Column('class', String)
    display_name = Column('display_name', String)
    source = Column('source', String)
    category = Column('category', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"ALIAS"}
        
    def __init__(self, class_type, display_name, source, category, date_created, created_by):
        self.class_type = class_type
        self.display_name = display_name
        self.source = source
        self.category = category
        self.date_created = date_created
        self.created_by = created_by
       
        
        
        
    
    
    