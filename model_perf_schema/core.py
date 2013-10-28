'''
Created on Oct 28, 2013

@author: kpaskov
'''

from model_perf_schema import EqualityByIDMixin, Base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, CLOB, String

class Bioentity(Base, EqualityByIDMixin):
        __tablename__ = 'bioentity'
    
        id = Column('bioentity_id', Integer, primary_key=True)
        json = Column('json', String)
        locustabs_json = Column('json', String)
                
        def __init__(self, bioentity_id, json, locustabs_json):
            self.bioentity_id = bioentity_id
            self.json = json
            self.locustabs_json = locustabs_json
        
class Bioconcept(Base, EqualityByIDMixin):
        __tablename__ = 'bioconcept'
    
        id = Column('bioconcept_id', Integer, primary_key=True)
        json = Column('json', String)
                
        def __init__(self, bioconcept_id, json):
            self.bioconcept_id = bioconcept_id
            self.json = json
        
class Reference(Base, EqualityByIDMixin):
        __tablename__ = 'reference'
    
        id = Column('bioentity_id', Integer, primary_key=True)
        json = Column('json', String)
        bibentry_json = Column('bibentry_json', CLOB)
                
        def __init__(self, bioentity_id, json, bibentry_json):
            self.bioentity_id = bioentity_id
            self.json = json
            self.bibentry_json = bibentry_json
        
class Disambig(Base, EqualityByIDMixin):
        __tablename__ = 'reference'
    
        id = Column('disambig_id', Integer, primary_key=True)
        disambig_key = Column('disambig_key', String)
        class_type = Column('class', String)
        subclass_type = Column('subclass', String)
        obj_id = Column('obj_id', Integer)
                
        def __init__(self, disambig_id, disambig_key, class_type, subclass_type, obj_id):
            self.disambig_id = disambig_id
            self.disambig_key = disambig_key
            self.class_type = class_type
            self.subclass_type = subclass_type
            self.obj_id = obj_id