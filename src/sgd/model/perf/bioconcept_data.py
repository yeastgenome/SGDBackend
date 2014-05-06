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

    def __init__(self, bioconcept_id, class_type, json):
        self.bioconcept_id = bioconcept_id
        self.class_type = class_type
        self.json = json

class BioconceptDetails(Base, EqualityByIDMixin):
    __tablename__ = 'bioconcept_details'

    id = Column('bioconcept_details_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, bioconcept_id, class_type, json):
        self.bioconcept_id = bioconcept_id
        self.class_type = class_type
        self.json = json

