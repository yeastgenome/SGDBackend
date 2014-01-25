'''
Created on Oct 28, 2013

@author: kpaskov
'''
from model_perf_schema import EqualityByIDMixin, Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String
from core import Bioconcept

class BioconceptGraph(Base, EqualityByIDMixin):
    __tablename__ = 'bioconcept_graph'

    id = Column('bioconcept_graph_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, bioconcept_id, class_type, json):
        self.bioconcept_id = bioconcept_id
        self.class_type = class_type
        self.json = json
