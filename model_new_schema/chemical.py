'''
Created on Jun 4, 2013

@author: kpaskov
'''
from model_new_schema import Base
from model_new_schema.misc import Alias, Altid
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Chemical(Base):
    __tablename__ = "chemical"
    
    id = Column('chemical_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    source = Column('source', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    def __init__(self, display_name, format_name, source, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.source = source
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name)
        
class ChemicalRelation(Base):
    __tablename__ = "chemicalrel"
    
    id = Column('chemicalrel_id', Integer, primary_key=True)
    parent_id = Column('parent_chemical_id', Integer, ForeignKey(Chemical.id))
    child_id = Column('child_chemical_id', Integer, ForeignKey(Chemical.id))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    parent = relationship(Chemical, uselist=False, primaryjoin="ChemicalRelation.parent_id==Chemical.id")
    child = relationship(Chemical, uselist=False, backref='parent_rels', primaryjoin="ChemicalRelation.child_id==Chemical.id")
          
    def __init__(self, chemicalrel_id, parent_id, child_id, date_created, created_by):
        self.id = chemicalrel_id
        self.parent_id = parent_id
        self.child_id = child_id
        self.date_created = date_created
        self.created_by = created_by  
        
    def unique_key(self):
        return (self.parent_id, self.child_id)  
        
class ChemicalAlias(Alias):
    __tablename__ = 'chemicalalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    
    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL_ALIAS',
                       'inherit_condition': id == Alias.id}
        
    #Relationships
    chemical = relationship(Chemical, uselist=False, backref=backref('aliases', passive_deletes=True))
        
    def __init__(self, name, source, chemical_id, date_created, created_by):
        Alias.__init__(self, name, 'CHEMICAL_ALIAS', source, None, date_created, created_by)
        self.chemical_id = chemical_id
        
    def unique_key(self):
        return (self.name, self.chemical_id)
    
class ChemicalAltid(Altid):
    __tablename__ = 'chemicalaltid'
    
    id = Column('altid_id', Integer, ForeignKey(Altid.id), primary_key=True)
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    
    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL_ALTID',
                       'inherit_condition': id == Altid.id}
        
    #Relationships
    chemical = relationship(Chemical, uselist=False, backref=backref('altids', passive_deletes=True))
        
    def __init__(self, identifier, source, altid_name, chemical_id, date_created, created_by):
        Altid.__init__(self, identifier, 'CHEMICAL_ALTID', source, altid_name, date_created, created_by)
        self.chemical_id = chemical_id
        
        
        