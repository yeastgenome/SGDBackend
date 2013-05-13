'''
Created on Feb 12, 2013

@author: kpaskov
'''
from model_new_schema import EqualityByIDMixin, Base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

class Typeahead(Base, EqualityByIDMixin):
    __tablename__ = 'typeahead3'
    
    id = Column('typeahead_id', Integer, primary_key=True)
    name = Column('name', String)
    full_name = Column('full_name', String)
    bio_type = Column('bio_type', String)
    bio_id = Column('bio_id', Integer)
    source = Column('source', String)
    use_for_typeahead = Column('use_for_typeahead', String)
    use_for_search = Column('use_for_search', String)
    
    def __init__(self, name, bio_type, bio_id, source):
        self.name = name
        #self.full_name = full_name
        self.bio_type = bio_type
        self.bio_id = bio_id
        self.source = source
        #self.use_for_typeahead = use_for_typeahead
       # self.use_for_search = use_for_search
    
    