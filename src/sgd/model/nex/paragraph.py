from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from bioentity import Bioentity
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.misc import Source
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateByJsonMixin


__author__ = 'kpaskov'

class Paragraph(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'paragraph'
    
    id = Column('paragraph_id', Integer, primary_key=True)
    class_type = Column('subclass', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', ForeignKey(Source.id))
    text = Column('text', CLOB)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref='paragraphs')
    references = association_proxy('paragraph_references', 'reference')
    source = relationship(Source, uselist=False, lazy='joined')

    __eq_values__ = ['id', 'class_type', 'format_name', 'display_name', 'link', 'text', 'date_created', 'created_by']
    __eq_fks__ = ['bioentity', 'source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        if 'bioentity' in obj_json:
            self.format_name = obj_json['bioentity'].format_name
            self.display_name = obj_json['class_type'] + ' ' + obj_json['bioentity'].display_name
        
    def unique_key(self):
        return self.format_name, self.class_type

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['references'] = sorted([x.to_semi_json() for x in self.references], key=lambda x: (x['year'], x['pubmed_id']), reverse=True)
        return obj_json
    
class ParagraphReference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'paragraph_reference'
    
    id = Column('paragraph_reference_id', Integer, primary_key=True)
    source_id = Column('source_id', ForeignKey(Source.id))
    paragraph_id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    class_type = Column('subclass', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    #Relationships
    paragraph = relationship(Paragraph, uselist=False, backref='paragraph_references')
    reference = relationship(Reference, uselist=False)
    source = relationship(Source, uselist=False, lazy='joined')

    __eq_values__ = ['id', 'class_type', 'date_created', 'created_by']
    __eq_fks__ = ['source', 'paragraph', 'reference']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        
    def unique_key(self):
        return self.paragraph_id, self.reference_id
