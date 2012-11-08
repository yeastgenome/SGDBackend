
'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Mapper style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import metadata
from sqlalchemy.orm import mapper
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer, String

bioentity = Table('BIOENT', metadata, 
                  Column('bioent_id', Integer, primary_key = True),
                  Column('name', String),
                  Column('bioent_type', String))

orf = Table('ORF', metadata, 
                  Column('bioent_id', Integer, ForeignKey('BIOENT.bioent_id'), primary_key = True),
                  Column('description', String))

crickorf = Table('CRICKORF', metadata, 
                  Column('bioent_id', Integer, ForeignKey('BIOENT.bioent_id'), ForeignKey('ORF.bioent_id'), primary_key = True),
                  Column('crick_data', String))

class Bioentity(object):
    def __init__(self, bioentity_id, name, bioent_type):
        self.id = id
        self.name = name
        self.type = bioent_type

mapper(Bioentity, bioentity, 
       properties={
            'id': bioentity.c.bioent_id,
            'name': bioentity.c.name,
            'type': bioentity.c.bioent_type
            },
        polymorphic_on = bioentity.c.bioent_type,
        polymorphic_identity = 'bioentity'
)

class Orf(Bioentity):
    def __init__(self, bioentity_id, name, bioent_type, description):
        super(Orf, self).__init__(id, name, bioent_type);
        self.description = description

mapper(Orf, orf, 
       properties={
            'id': [orf.c.bioent_id, bioentity.c.bioent_id],
            'description': orf.c.description
            },
       inherits = Bioentity,
       polymorphic_identity = 'ORF',
)

class Crickorf(Orf):
    def __init__(self, bioentity_id, name, bioent_type, description, crick_data):
        super(Bioentity, self).__init__(id, name, bioent_type, description);
        self.crick_data = crick_data

mapper(Crickorf, crickorf, 
       properties={
            'id': [crickorf.c.bioent_id, orf.c.bioent_id, bioentity.c.bioent_id],
            'crick_data': crickorf.c.crick_data
            },
       inherits = Orf,
       polymorphic_identity = 'Crick'
)



