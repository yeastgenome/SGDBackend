'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.misc import Url, Alias
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Bioconcept(Base, EqualityByIDMixin):
    __tablename__ = "bioconcept"
        
    id = Column('bioconcept_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    sgdid = Column('sgdid', String)
    description = Column('description', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"BIOCONCEPT"}
    
    def __init__(self, bioconcept_id, display_name, format_name, class_type, link, source, sgdid, description, date_created, created_by):
        self.id = bioconcept_id
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.sgdid = sgdid
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.class_type)
      
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
    
class Bioconcepturl(Url):
    __tablename__ = 'bioconcepturl'
    
    url_id = Column('url_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
        
    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Url.id}
    
    def __init__(self, display_name, link, source, category, bioconcept, date_created, created_by):
        Url.__init__(self, display_name, bioconcept.format_name, 'BIOCONCEPT', link, source, category, 
                     bioconcept.id, date_created, created_by)
        self.bioconcept_id = bioconcept.id
    
class Bioconceptalias(Alias):
    __tablename__ = 'bioconcepturl'
    
    alias_id = Column('alias_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))

    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, bioconcept, date_created, created_by):
        Alias.__init__(self, display_name, bioconcept.format_name, 'BIOCONCEPT', source, category, date_created, created_by)
        self.bioconcept_id = bioconcept.id

    
    
    
    
    




    