from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base, JsonMixins
from src.sgd.model import EqualityByIDMixin


__author__ = 'kpaskov'

class Bioentity(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'bioentity'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    json = Column('json', String)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Bioconcept(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'bioconcept'
    
    id = Column('bioconcept_id', Integer, primary_key=True)
    json = Column('json', CLOB)
                
    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)
        
class Reference(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'reference'
    
    id = Column('reference_id', Integer, primary_key=True)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Bioitem(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'bioitem'

    id = Column('bioitem_id', Integer, primary_key=True)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Author(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'author'

    id = Column('author_id', Integer, primary_key=True)
    json = Column('json', String)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Ontology(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'ontology'

    id = Column('ontology_id', Integer, primary_key=True)
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Disambig(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'disambig'
    
    id = Column('disambig_id', Integer, primary_key=True)
    disambig_key = Column('disambig_key', String)
    class_type = Column('class', String)
    subclass_type = Column('subclass', String)
    obj_id = Column('obj_id', Integer)
                
    def __init__(self, disambig_id, disambig_key, class_type, subclass_type, obj_id):
        self.id = disambig_id
        self.disambig_key = disambig_key
        self.class_type = class_type
        self.subclass_type = subclass_type
        self.obj_id = obj_id

    @classmethod
    def from_json(cls, obj_json):
        return cls(obj_json['id'], obj_json['disambig_key'], obj_json['class_type'], obj_json['subclass_type'], obj_json['identifier'])