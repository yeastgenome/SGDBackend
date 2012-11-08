'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Bioentity(Base):
    __tablename__ = "bioent"
    
    id = Column('bioent_id', Integer, primary_key = True)
    name = Column('name', String)
    bioentity_type = Column('bioent_type', String)
    
    __mapper_args__ = {'polymorphic_on': bioentity_type,
                       'polymorphic_identity':"Bioentity"}

class Orf(Bioentity):
    __tablename__ = "orf"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key = True)
    description = Column('description', String)
    
    __mapper_args__ = {'polymorphic_identity': "ORF",
                       'inherit_condition': id == Bioentity.id}

class Crickorf(Orf):
    __tablename__ = "crickorf"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), ForeignKey(Orf.id), primary_key = True)
    crick_data = Column('crick_data', String)

    __mapper_args__ = {'polymorphic_identity': "Crick",
                       'inherit_condition':id == Bioentity.id == Orf.id}
    
class NotPhysicallyMapped(Bioentity):
    __mapper_args__ = {'polymorphic_identity': "not physically mapped"}