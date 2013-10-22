'''
Created on Oct 21, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioentity import Bioentity
from model_new_schema.reference import Reference
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB

class Paragraph(Base, EqualityByIDMixin):
    __tablename__ = 'paragraph'
    
    id = Column('paragraph_id', Integer, primary_key=True)
    class_type = Column('class', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    text = Column('text', CLOB)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    references = association_proxy('paragraph_references', 'reference')
        
    def __init__(self, class_type, bioentity, text, date_created, created_by):
        self.class_type = class_type
        self.bioentity_id = bioentity.id
        self.text = text
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.class_type, self.bioentity_id)
    
class ParagraphReference(Base, EqualityByIDMixin):
    __tablename__ = 'paragraph_reference'
    
    id = Column('paragraph_reference_id', Integer, primary_key=True)
    paragraph_id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    class_type = Column('class', String)
    
    #Relationships
    paragraph = relationship(Paragraph, uselist=False, backref='paragraph_references')
    reference = relationship(Reference, uselist=False)
        
    def __init__(self, paragraph_id, reference_id, class_type):
        self.paragraph_id = paragraph_id
        self.reference_id = reference_id
        self.class_type = class_type
        
    def unique_key(self):
        return (self.paragraph_id, self.reference_id)