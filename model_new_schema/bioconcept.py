'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.config import SCHEMA
from model_new_schema.link_maker import add_link, biocon_link
from model_new_schema.misc import Alias
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date


class Bioconcept(Base, EqualityByIDMixin):
    __tablename__ = "biocon"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
        
    id = Column('biocon_id', Integer, primary_key = True)
    biocon_type = Column('biocon_type', String)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    description = Column('description', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    type = "BIOCONCEPT"
    
    __mapper_args__ = {'polymorphic_on': biocon_type,
                       'polymorphic_identity':"BIOCONCEPT"}
    
    #Relationships
    aliases = association_proxy('bioconaliases', 'name')
    
    def __init__(self, biocon_id, biocon_type, display_name, format_name, description, date_created, created_by):
        self.id = biocon_id
        self.biocon_type = biocon_type
        self.display_name = display_name
        self.format_name = format_name
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.biocon_type)
            
    @hybrid_property
    def link(self):
        return biocon_link(self)
    @hybrid_property
    def name_with_link(self):
        return add_link(self.display_name, self.link)
    @hybrid_property
    def alias_str(self):
        return ', '.join(self.aliases)
    @hybrid_property
    def search_entry_title(self):
        return self.name_with_link
    @hybrid_property
    def search_description(self):
        return self.description
    @hybrid_property
    def search_additional(self):
        return None
      
class BioconRelation(Base, EqualityByIDMixin):
    __tablename__ = 'bioconrel'

    id = Column('biocon_biocon_id', Integer, primary_key=True)
    parent_id = Column('parent_biocon_id', Integer, ForeignKey(Bioconcept.id))
    child_id = Column('child_biocon_id', Integer, ForeignKey(Bioconcept.id))
    relationship_type = Column('relationship_type', String)
    bioconrel_type = Column('bioconrel_type', String)
   
    parent_biocon = relationship('Bioconcept', uselist=False, backref=backref('child_biocons', cascade='all,delete'), primaryjoin="BioconRelation.parent_id==Bioconcept.id")
    child_biocon = relationship('Bioconcept', uselist=False, backref=backref('parent_biocons', cascade='all,delete'), primaryjoin="BioconRelation.child_id==Bioconcept.id")
    type = "BIOCON_BIOCON"

    def __init__(self, parent_id, child_id, bioconrel_type, relationship_type):
        self.parent_id = parent_id
        self.child_id = child_id
        self.bioconrel_type = bioconrel_type
        self.relationship_type = relationship_type
        
    def unique_key(self):
        return (self.parent_id, self.child_id, self.bioconrel_type, self.relationship_type)
        
  
class BioconAncestor(Base, EqualityByIDMixin):
    __tablename__ = 'biocon_ancestor'

    id = Column('biocon_ancestor_id', Integer, primary_key=True)
    ancestor_id = Column('ancestor_biocon_id', Integer, ForeignKey(Bioconcept.id))
    child_id = Column('child_biocon_id', Integer, ForeignKey(Bioconcept.id))
    generation = Column('generation', Integer)
    bioconanc_type = Column('bioconanc_type', String)
   
    ancestor_biocon = relationship('Bioconcept', uselist=False, backref=backref('child_family', cascade='all,delete'), primaryjoin="BioconAncestor.ancestor_id==Bioconcept.id")
    child_biocon = relationship('Bioconcept', uselist=False, backref=backref('parent_family', cascade='all,delete'), primaryjoin="BioconAncestor.child_id==Bioconcept.id")
    type = "BIOCON_ANCESTOR"

    def __init__(self, ancestor_id, child_id, bioconanc_type, generation):
        self.ancestor_id = ancestor_id
        self.child_id = child_id
        self.bioconanc_type = bioconanc_type
        self.generation = generation

    def unique_key(self):
        return (self.ancestor_id, self.child_id, self.bioconanc_type)
    
class BioconAlias(Alias):
    __tablename__ = 'bioconalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    biocon_id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id))
    biocon_type = Column('biocon_type', String)
    
    __mapper_args__ = {'polymorphic_identity': 'BIOCON_ALIAS',
                       'inherit_condition': id == Alias.id}
        
    #Relationships
    biocon = relationship(Bioconcept, uselist=False, backref=backref('bioconaliases', passive_deletes=True))
        
    def __init__(self, name, biocon_id, biocon_type, date_created, created_by):
        Alias.__init__(self, name, 'BIOCON_ALIAS', None, None, date_created, created_by)
        self.biocon_id = biocon_id
        self.biocon_type = biocon_type
        
    def unique_key(self):
        return (self.name, self.biocon_id)
    
    
    
    
    
    




    