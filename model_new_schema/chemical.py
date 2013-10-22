'''
Created on Jun 4, 2013

@author: kpaskov
'''
from model_new_schema import Base, create_format_name
from model_new_schema.misc import Alias
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Chemical(Base):
    __tablename__ = "chemical"
    
    id = Column('chemical_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    def __init__(self, display_name, source, date_created, created_by):
        self.display_name = display_name
        self.format_name = create_format_name(display_name)
        self.link = None
        self.source_id = source.id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    
    
class Chemicalalias(Alias):
    __tablename__ = 'chemicalalias'
    
    alias_id = Column('alias_id', Integer, primary_key=True)
    chemical_id = Column('bioconcept_id', Integer, ForeignKey(Chemical.id))

    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, chemical, date_created, created_by):
        Alias.__init__(self, display_name, chemical.format_name, 'CHEMICAL', source, category, date_created, created_by)
        self.chemical_id = chemical.id
        
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
        
        
        