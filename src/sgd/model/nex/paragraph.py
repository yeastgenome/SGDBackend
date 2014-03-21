from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from bioentity import Bioentity
from src.sgd.model.nex.reference import Reference
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base


__author__ = 'kpaskov'

class Paragraph(Base, EqualityByIDMixin):
    __tablename__ = 'paragraph'
    
    id = Column('paragraph_id', Integer, primary_key=True)
    class_type = Column('subclass', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    text = Column('text', CLOB)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    #Relationships
    bioentity = relationship(Bioentity, uselist=False)
    references = association_proxy('paragraph_references', 'reference')
        
    def __init__(self, class_type, source, bioentity, text, date_created, created_by):
        self.display_name = class_type + ' ' + bioentity.display_name
        self.format_name = bioentity.format_name
        self.link = None
        self.source_id = source.id
        self.class_type = class_type
        self.bioentity_id = bioentity.id
        self.text = text
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.class_type)

    def to_json(self):
        return {
                'text': self.text,
                'references': sorted([x.to_json() for x in self.references], key=lambda x: (x['year'], x['pubmed_id']), reverse=True)
               }
    
class ParagraphReference(Base, EqualityByIDMixin):
    __tablename__ = 'paragraph_reference'
    
    id = Column('paragraph_reference_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer)
    paragraph_id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    class_type = Column('subclass', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    #Relationships
    paragraph = relationship(Paragraph, uselist=False, backref='paragraph_references')
    reference = relationship(Reference, uselist=False)
        
    def __init__(self, source, paragraph, reference, class_type, date_created, created_by):
        self.source_id = source.id
        self.paragraph_id = paragraph.id
        self.reference_id = reference.id
        self.class_type = class_type
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.paragraph_id, self.reference_id)
    