from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base, JsonMixins
from src.sgd.model import EqualityByIDMixin


__author__ = 'kpaskov'

class Bioentity(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'bioentity'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Locustab(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'locustab'

    id = Column('bioentity_id', Integer, primary_key=True)
    json = Column('json', String)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Locusentry(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'locusentry'

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

class Bibentry(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'bibentry'

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
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Experiment(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'experiment'

    id = Column('experiment_id', Integer, primary_key=True)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Tag(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'tag'

    id = Column('tag_id', Integer, primary_key=True)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Strain(Base, EqualityByIDMixin, JsonMixins):
    __tablename__ = 'strain'

    id = Column('strain_id', Integer, primary_key=True)
    json = Column('json', CLOB)

    def __init__(self, obj_json):
        JsonMixins.__init__(self, obj_json)

class Orphan(Base, EqualityByIDMixin):
    __tablename__ = 'orphan'

    id = Column('orphan_id', Integer, primary_key=True)
    url = Column('url', String)
    json = Column('json', CLOB)

    def __init__(self, url, json):
        self.url = url
        self.json = json

class Disambig(Base, EqualityByIDMixin):
    __tablename__ = 'disambig'
    
    id = Column('disambig_id', Integer, primary_key=True)
    disambig_key = Column('disambig_key', String)
    class_type = Column('class', String)
    subclass_type = Column('subclass', String)
    obj_id = Column('obj_id', Integer)
                
    def __init__(self, obj_json):
        self.disambig_key = obj_json['disambig_key'].lower()
        self.class_type = obj_json['class_type']
        self.subclass_type = obj_json['subclass_type']
        self.obj_id = obj_json['identifier']

    def update(self, obj_json):
        changed = False
        if obj_json['identifier'] != self.obj_id:
            self.obj_id = obj_json['identifier']
            changed = True
        return changed

    def to_json(self):
        return {'id': (self.class_type, self.subclass_type, self.disambig_key),
                'disambig_key': self.disambig_key,
                'class_type': self.class_type,
                'subclass_type': self.subclass_type,
                'identifier': self.obj_id}
