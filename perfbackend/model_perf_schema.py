'''
Created on Oct 28, 2013

@author: kpaskov
'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, CLOB

class EqualityByIDMixin(object):
    def __eq__(self, other):
        if type(other) is type(self):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

SCHEMA = None  
Base = None
metadata = None

def perf_factory(tablename, ) :
    class NewClass(Base, EqualityByIDMixin):
        __tablename__ = tablename
    
        bioentity_id = Column('bioentity_id', Integer, primary_key=True)
        json = Column('json', CLOB)
                
        def __init__(self, bioentity_id, json):
            self.bioentity_id = bioentity_id
            self.json = json
            
        @hybrid_property
        def id(self):
            return self.bioentity_id
                
        def unique_key(self):
            return self.bioentity_id
    
    NewClass.__name__ = tablename.title().replace('_', '')
    return NewClass