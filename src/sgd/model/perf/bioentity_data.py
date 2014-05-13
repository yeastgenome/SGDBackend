from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base
from core import Bioentity
from src.sgd.model import EqualityByIDMixin


__author__ = 'kpaskov'

class BioentityGraph(Base, EqualityByIDMixin):
    __tablename__ = 'bioentity_graph'

    id = Column('bioentity_graph_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        self.bioentity_id = obj_json['bioentity_id']
        self.class_type = obj_json['class_type']
        self.json = obj_json['json']

    def update(self, obj_json):
        self.json = obj_json['json']
        return True

    def to_json(self):
        return {'id': (self.class_type, self.bioentity_id),
                    'bioentity_id': self.bioentity_id,
                    'class_type': self.disambig_key,
                    'json': self.json}

class BioentityEnrichment(Base, EqualityByIDMixin):
    __tablename__ = 'bioentity_enrichment'

    id = Column('bioentity_enrichment_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        self.bioentity_id = obj_json['bioentity_id']
        self.class_type = obj_json['class_type']
        self.json = obj_json['json']

    def update(self, obj_json):
        self.json = obj_json['json']
        return True

    def to_json(self):
        return {'id': (self.class_type, self.bioentity_id),
                    'bioentity_id': self.bioentity_id,
                    'class_type': self.disambig_key,
                    'json': self.json}

class BioentityDetails(Base, EqualityByIDMixin):
    __tablename__ = 'bioentity_details'

    id = Column('bioentity_details_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        self.bioentity_id = obj_json['bioentity_id']
        self.class_type = obj_json['class_type']
        self.json = obj_json['json']

    def update(self, obj_json):
        self.json = obj_json['json']
        return True

    def to_json(self):
            return {'id': (self.class_type, self.bioentity_id),
                    'bioentity_id': self.bioentity_id,
                    'class_type': self.disambig_key,
                    'json': self.json}