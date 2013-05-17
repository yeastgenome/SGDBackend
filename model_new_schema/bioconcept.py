'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.config import SCHEMA
from model_new_schema.link_maker import add_link, biocon_link
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Bioconcept(Base, EqualityByIDMixin):
    __tablename__ = "biocon"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
        
    id = Column('biocon_id', Integer, primary_key = True)
    biocon_type = Column('biocon_type', String)
    official_name = Column('name', String)

    type = "BIOCONCEPT"
    description = Column('description', String)
    
    __mapper_args__ = {'polymorphic_on': biocon_type,
                       'polymorphic_identity':"BIOCONCEPT",
                       'with_polymorphic':'*'}
    
    def __init__(self, biocon_id, biocon_type, official_name, description, date_created, created_by):
        self.id = biocon_id
        self.biocon_type = biocon_type
        self.official_name = official_name
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
            
    @hybrid_property
    def link(self):
        return biocon_link(self)
    @hybrid_property
    def name(self):
        return self.official_name.replace('_', ' ')
    @hybrid_property
    def name_with_link(self):
        return add_link(self.name, self.link)
    
    @hybrid_property
    def search_entry_title(self):
        return self.name_with_link
    @hybrid_property
    def search_description(self):
        return self.description
    @hybrid_property
    def search_additional(self):
        return None
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.official_name
        return '%s(id=%s, name=%s)' % data
      





    