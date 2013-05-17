'''
Created on Mar 4, 2013

@author: kpaskov
'''
from model_new_schema import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Chemical(Base):
    __tablename__ = "chemical"
    
    id = Column('chemical_id', Integer, primary_key=True)
    name = Column('name', String)
    
    def __init__(self, name):
        self.name = name

class Allele(Base):
    __tablename__ = 'allele'
    id = Column('allele_id', Integer, primary_key=True)
    official_name = Column('name', String)
    parent_id = Column('parent_bioent_id', Integer, ForeignKey('sprout.bioent.bioent_id'))
    more_info = Column('description', String)
    
    @hybrid_property
    def name(self):
        return self.official_name
    
    @hybrid_property
    def description(self):
        return 'Allele'
    
    def __init__(self, name, description):
        self.official_name = name
        self.more_info = description