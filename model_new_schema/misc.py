'''
Created on Mar 4, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

class Url(Base):
    __tablename__ = 'url'
    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    category = Column('category', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"URL"}
    
    def __init__(self, display_name, format_name, class_type, link, source, category, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.category = category
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.link, self.format_name)
    
class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'
    
    id = Column('alias_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    source_id = Column('source_id', Integer)
    category = Column('category', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"ALIAS"}
        
    def __init__(self, display_name, format_name, class_type, source, category, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.source_id = source.id
        self.category = category
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.display_name, self.format_name)
    
class Relation(Base, EqualityByIDMixin):
    __tablename__ = 'relation'
    
    id = Column('relation_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    source_id = Column('source_id', Integer, ForeignKey('nex.source.source_id'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"RELATION"}
        
    def __init__(self, display_name, format_name, class_type, source, relation_type, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.source_id = source.id
        self.relation_type = relation_type
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.class_type, self.relation_type)
       

    
    