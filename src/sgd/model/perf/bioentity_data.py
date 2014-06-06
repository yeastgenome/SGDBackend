from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base
from core import Bioentity
from src.sgd.model import EqualityByIDMixin


__author__ = 'kpaskov'

class BioentityGraph(Base):
    __tablename__ = 'bioentity_graph'

    id = Column('bioentity_graph_id', Integer, primary_key=True)
    obj_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, bioentity_id, class_type, json):
        self.obj_id = bioentity_id
        self.class_type = class_type
        self.json = json

class BioentityEnrichment(Base):
    __tablename__ = 'bioentity_enrichment'

    id = Column('bioentity_enrichment_id', Integer, primary_key=True)
    obj_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, bioentity_id, class_type, json):
        self.obj_id = bioentity_id
        self.class_type = class_type
        self.json = json

class BioentityDetails(Base):
    __tablename__ = 'bioentity_details'

    id = Column('bioentity_details_id', Integer, primary_key=True)
    obj_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, bioentity_id, class_type, json):
        self.obj_id = bioentity_id
        self.class_type = class_type
        self.json = json