from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base
from core import Bioconcept
from src.sgd.model import EqualityByIDMixin


__author__ = 'kpaskov'

class BioconceptGraph(Base, EqualityByIDMixin):
    __tablename__ = 'bioconcept_graph'

    id = Column('bioconcept_graph_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        self.bioconcept_id = obj_json['bioconcept_id']
        self.class_type = obj_json['class_type']
        self.json = obj_json['json']

    def update(self, obj_json):
        self.json = obj_json['json']
        return True

    def to_json(self):
        return {'id': (self.class_type, self.bioconcept_id),
                    'bioconcept_id': self.bioconcept_id,
                    'class_type': self.disambig_key,
                    'json': self.json}

class BioconceptDetails(Base, EqualityByIDMixin):
    __tablename__ = 'bioconcept_details'

    id = Column('bioconcept_details_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        self.bioconcept_id = obj_json['bioconcept_id']
        self.class_type = obj_json['class_type']
        self.json = obj_json['json']

    def update(self, obj_json):
        self.json = obj_json['json']
        return True

    def to_json(self):
        return {'id': (self.class_type, self.bioconcept_id),
                    'bioconcept_id': self.bioconcept_id,
                    'class_type': self.disambig_key,
                    'json': self.json}

