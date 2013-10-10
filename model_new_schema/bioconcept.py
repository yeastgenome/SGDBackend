'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.misc import Alias
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Bioconcept(Base, EqualityByIDMixin):
    __tablename__ = "bioconcept"
        
    id = Column('bioconcept_id', Integer, primary_key = True)
    class_type = Column('class', String)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_link', String)
    description = Column('description', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"BIOCONCEPT"}
    
    #Relationships
    aliases = association_proxy('bioconceptaliases', 'name')
    
    def __init__(self, bioconcept_id, class_type, display_name, format_name, link, description, date_created, created_by):
        self.id = bioconcept_id
        self.class_type = class_type
        self.display_name = display_name
        self.format_name = format_name
        self.link = link
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.class_type)
            
    @hybrid_property
    def alias_str(self):
        return ', '.join(self.aliases)
      
class BioconceptRelation(Base, EqualityByIDMixin):
    __tablename__ = 'bioconcept_relation'

    id = Column('bioconcept_relation_id', Integer, primary_key=True)
    parent_bioconcept_id = Column('parent_bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    child_bioconcept_id = Column('child_bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    relationship_type = Column('relationship_type', String)
    class_type = Column('class', String)
   
    #Relationships
    parent_bioconcept = relationship('Bioconcept', uselist=False, backref=backref('child_bioconcepts', cascade='all,delete'), primaryjoin="BioconceptRelation.parent_bioconcept_id==Bioconcept.id")
    child_bioconcept = relationship('Bioconcept', uselist=False, backref=backref('parent_bioconcepts', cascade='all,delete'), primaryjoin="BioconceptRelation.child_bioconcept_id==Bioconcept.id")

    def __init__(self, parent_bioconcept_id, child_bioconcept_id, class_type, relationship_type):
        self.parent_bioconcept_id = parent_bioconcept_id
        self.child_bioconcept_id = child_bioconcept_id
        self.class_type = class_type
        self.relationship_type = relationship_type
        
    def unique_key(self):
        return (self.parent_bioconcept_id, self.child_bioconcept_id, self.class_type, self.relationship_type)
    
class Bioconceptalias(Alias):
    __tablename__ = 'bioconceptalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    class_type = Column('class', String)
    
    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Alias.id}
        
    #Relationships
    bioconcept = relationship(Bioconcept, uselist=False, backref=backref('bioconceptaliases', passive_deletes=True))
        
    def __init__(self, display_name, bioconcept_id, class_type, date_created, created_by):
        Alias.__init__(self, 'BIOCONCEPT', display_name, None, None, date_created, created_by)
        self.bioconcept_id = bioconcept_id
        self.class_type = class_type
        
    def unique_key(self):
        return (self.display_name, self.bioconcept_id)
    
    
    
    
    
    




    