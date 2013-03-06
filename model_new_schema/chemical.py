'''
Created on Mar 4, 2013

@author: kpaskov
'''
from model_new_schema import Base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

class Chemical(Base):
    __tablename__ = "chemical"
    
    id = Column('chemical_id', Integer, primary_key=True)
    name = Column('name', String)
    
    def __init__(self, name):
        self.name = name
