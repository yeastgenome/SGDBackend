'''
Created on Jun 4, 2013

@author: kpaskov
'''
from model_new_schema import Base
from model_new_schema.misc import Alias
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Chemical(Base):
    __tablename__ = "chemical"
    
    id = Column('chemical_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_link', String)
    source = Column('source', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    aliases = association_proxy('chemicalaliases', 'name')
    
    def __init__(self, display_name, format_name, link, source, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.link = link
        self.source = source
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    
    @hybrid_property
    def alias_str(self):
        return ', '.join(self.aliases)      
        
class ChemicalRelation(Base):
    __tablename__ = "chemical_relation"
    
    id = Column('chemical_relation_id', Integer, primary_key=True)
    parent_chemical_id = Column('parent_chemical_id', Integer, ForeignKey(Chemical.id))
    child_chemical_id = Column('child_chemical_id', Integer, ForeignKey(Chemical.id))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    parent = relationship(Chemical, uselist=False, primaryjoin="ChemicalRelation.parent_chemical_id==Chemical.id")
    child = relationship(Chemical, uselist=False, backref='parent_chemical_relations', primaryjoin="ChemicalRelation.child_chemical_id==Chemical.id")
          
    def __init__(self, chemical_relation_id, parent_chemical_id, child_chemical_id, date_created, created_by):
        self.id = chemical_relation_id
        self.parent_chemical_id = parent_chemical_id
        self.child_chemical_id = child_chemical_id
        self.date_created = date_created
        self.created_by = created_by  
        
    def unique_key(self):
        return (self.parent_chemical_id, self.child_chemical_id)  
        
class ChemicalAlias(Alias):
    __tablename__ = 'chemicalalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    
    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL',
                       'inherit_condition': id == Alias.id}
        
    #Relationships
    chemical = relationship(Chemical, uselist=False, backref=backref('chemicalaliases', passive_deletes=True))
        
    def __init__(self, display_name, source, chemical_id, date_created, created_by):
        Alias.__init__(self, 'CHEMICAL', display_name, source, None, date_created, created_by)
        self.chemical_id = chemical_id
        
    def unique_key(self):
        return (self.display_name, self.chemical_id)
        
        
        