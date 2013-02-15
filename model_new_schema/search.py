'''
Created on Feb 12, 2013

@author: kpaskov
'''
from model_new_schema import EqualityByIDMixin, Base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Typeahead(Base, EqualityByIDMixin):
    __tablename__ = 'typeahead'
    
    id = Column('typeahead_id', Integer, primary_key=True)
    name = Column('name', String)
    full_name = Column('full_name', String)
    bio_type = Column('bio_type', String)
    bio_id = Column('bio_id', Integer, ForeignKey('sprout.bioent.bioent_id'))
    
    #Relationships
    bio = relationship('Bioentity', uselist=False)
    
    def __init__(self, name, full_name, bio_type, bio_id):
        self.name = name
        self.full_name = full_name
        self.bio_type = bio_type
        self.bio_id = bio_id
    
    