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

        def __init__(self, bioentity_id, class_type, json):
            self.bioentity_id = bioentity_id
            self.class_type = class_type
            self.json = json

        def __init__(self, obj_json):
            self.bioentity_id = obj_json['id']
            self.class_type = obj_json['class_type']
            self.json = obj_json['json']
            self.obj_id = obj_json['identifier']

        def update(self, obj_json):
            changed = False
            if obj_json['disambig_key'] != self.id:
                self.disambig_key = obj_json['disambig_key']
                changed = True
            if obj_json['class_type'] != self.id:
                self.class_type = obj_json['class_type']
                changed = True
            if obj_json['subclass_type'] != self.id:
                self.subclass_type = obj_json['subclass_type']
                changed = True
            if obj_json['obj_id'] != self.id:
                self.obj_id = obj_json['obj_id']
                changed = True
            return changed

        def to_json(self):
            return {'id': (self.class_type, self.subclass_type, self.obj_id),
                    'disambig_key': self.disambig_key,
                    'class_type': self.class_type,
                    'subclass_type': self.subclass_type,
                    'identifier': self.obj_id}

class BioentityEnrichment(Base, EqualityByIDMixin):
        __tablename__ = 'bioentity_enrichment'

        id = Column('bioentity_enrichment_id', Integer, primary_key=True)
        bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
        class_type = Column('class', String)
        json = Column('json', CLOB)

        def __init__(self, bioentity_id, class_type, json):
            self.bioentity_id = bioentity_id
            self.class_type = class_type
            self.json = json

class BioentityParagraph(Base, EqualityByIDMixin):
        __tablename__ = 'bioentity_paragraph'

        id = Column('bioentity_paragraph_id', Integer, primary_key=True)
        bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
        class_type = Column('class', String)
        json = Column('json', CLOB)

        def __init__(self, bioentity_id, class_type, json):
            self.bioentity_id = bioentity_id
            self.class_type = class_type
            self.json = json

class BioentityDetails(Base, EqualityByIDMixin):
        __tablename__ = 'bioentity_details'

        id = Column('bioentity_details_id', Integer, primary_key=True)
        bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
        class_type = Column('class', String)
        json = Column('json', CLOB)

        def __init__(self, bioentity_id, class_type, json):
            self.bioentity_id = bioentity_id
            self.class_type = class_type
            self.json = json