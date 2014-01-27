'''
Created on Oct 28, 2013

@author: kpaskov
'''
from model_perf_schema import EqualityByIDMixin, Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String
from core import Bioentity

class BioentityOverview(Base, EqualityByIDMixin):
        __tablename__ = 'bioentity_overview'

        id = Column('bioentity_overview_id', Integer, primary_key=True)
        bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
        class_type = Column('class', String)
        json = Column('json', String)

        def __init__(self, bioentity_id, class_type, json):
            self.bioentity_id = bioentity_id
            self.class_type = class_type
            self.json = json

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

class BioentityResources(Base, EqualityByIDMixin):
        __tablename__ = 'bioentity_resources'

        id = Column('bioentity_resources_id', Integer, primary_key=True)
        bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
        class_type = Column('class', String)
        json = Column('json', String)

        def __init__(self, bioentity_id, class_type, json):
            self.bioentity_id = bioentity_id
            self.class_type = class_type
            self.json = json

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
        json = Column('json', String)

        def __init__(self, bioentity_id, class_type, json):
            self.bioentity_id = bioentity_id
            self.class_type = class_type
            self.json = json