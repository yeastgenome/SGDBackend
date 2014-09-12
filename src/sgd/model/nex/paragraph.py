from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.misc import Strain, Source
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateByJsonMixin

__author__ = 'kpaskov'

class Paragraph(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'paragraph'

    id = Column('paragraph_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    category = Column('category', String)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    display_name = None
    link = None

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')

    __mapper_args__ = {'polymorphic_on': class_type}
    __eq_values__ = ['id', 'class_type', 'format_name', 'category', 'text', 'html', 'date_created', 'created_by']
    __eq_fks__ = ['source']

    def unique_key(self):
        return self.format_name, self.class_type, self.category

    def to_json(self, linkit=False):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['references'] = sorted([x.reference.to_semi_json() for x in self.paragraph_references], key=lambda x: (x['year'], x['pubmed_id']), reverse=True)
        if linkit:
            obj_json['text'] = obj_json['html']
        del obj_json['html']
        return obj_json
    
class ParagraphReference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'paragraph_reference'
    
    id = Column('paragraph_reference_id', Integer, primary_key=True)
    paragraph_id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    
    #Relationships
    paragraph = relationship(Paragraph, uselist=False, backref=backref('paragraph_references', passive_deletes=True))
    reference = relationship(Reference, uselist=False, backref=backref('paragraph_references', passive_deletes=True))

    __eq_values__ = ['id', 'paragraph_id', 'reference_id']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        
    def unique_key(self):
        return self.paragraph_id, self.reference_id

class Bioentityparagraph(Paragraph):
    __tablename__ = 'bioentityparagraph'

    id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('paragraphs', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "BIOENTITY", 'inherit_condition': id==Paragraph.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'category', 'text', 'html', 'date_created', 'created_by']
    __eq_fks__ = ['source', 'bioentity']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = obj_json['bioentity'].format_name

class Strainparagraph(Paragraph):
    __tablename__ = 'strainparagraph'

    id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id), primary_key=True)
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))

    #Relationships
    strain = relationship(Strain, uselist=False, backref=backref('paragraphs', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "STRAIN", 'inherit_condition': id==Paragraph.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'category', 'text', 'html', 'date_created', 'created_by']
    __eq_fks__ = ['source', 'strain']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = obj_json['strain'].format_name

class Referenceparagraph(Paragraph):
    __tablename__ = 'referenceparagraph'

    id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id), primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('paragraphs', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "REFERENCE", 'inherit_condition': id==Paragraph.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'category', 'text', 'html', 'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = obj_json['reference'].format_name


