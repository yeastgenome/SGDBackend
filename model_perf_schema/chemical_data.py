'''
Created on Oct 28, 2013

@author: kpaskov
'''
from model_perf_schema import EqualityByIDMixin, Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String
from core import Chemical

class ChemicalDetails(Base, EqualityByIDMixin):
    __tablename__ = 'chemical_details'

    id = Column('chemical_details_id', Integer, primary_key=True)
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, chemical_id, class_type, json):
        self.chemical_id = chemical_id
        self.class_type = class_type
        self.json = json
