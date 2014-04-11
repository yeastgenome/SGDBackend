from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

from bioconcept import Go
from src.sgd.model.nex.misc import Alias, Url, Relation, Source
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin


__author__ = 'kpaskov'

class Bioentity(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'bioentity'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    sgdid = Column('sgdid', String)
    uniprotid = Column('uniprotid', String)
    bioent_status = Column('bioent_status', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    
    __mapper_args__ = {'polymorphic_on': class_type}
            
    def unique_key(self):
        return self.format_name, self.class_type
    
class Bioentityurl(Url):
    __tablename__ = 'bioentityurl'
    
    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('urls', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == Url.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioentity_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioentity_id'))

class Bioentityalias(Alias):
    __tablename__ = 'bioentityalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    is_external_id = Column('is_external_id', Integer)

    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == Alias.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioentity_id', 'is_external_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioentity_id'))

class Bioentityrelation(Relation):
    __tablename__ = 'bioentityrelation'

    id = Column('relation_id', Integer, ForeignKey(Relation.id), primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioentity.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    parent = relationship(Bioentity, backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Bioentity, backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    
    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == Relation.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relation_type',
                     'parent_id', 'child_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))
        self.display_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))

class Locus(Bioentity):
    __tablename__ = "locusbioentity"
    
    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    locus_type = Column('locus_type', String)
    gene_name = Column('gene_name', String)
        
    __mapper_args__ = {'polymorphic_identity': 'LOCUS', 'inherit_condition': id == Bioentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status',
                     'description',
                     'name_description', 'headline', 'locus_type', 'gene_name',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.link = None if obj_json.get('sgdid') is None else '/cgi-bin/locus.fpl?locus=' + obj_json.get('sgdid')
    
class Protein(Bioentity):
    __tablename__ = "proteinbioentity"

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))

    #Relationships
    locus = relationship(Locus, uselist=False, foreign_keys=[locus_id])

    __mapper_args__ = {'polymorphic_identity': 'PROTEIN', 'inherit_condition': id == Bioentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status',
                     'description',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'locus']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        locus = obj_json.get('locus')
        if locus is not None:
            self.display_name = None if locus is None else locus.display_name + 'p'
            self.format_name = None if locus is None else locus.format_name + 'P'
            self.link = None if locus is None else '/locus/' + locus.sgdid + '/overview'
            self.bioent_status = None if locus is None else locus.bioent_status
            self.description = None if locus is None else locus.description

class Transcript(Bioentity):
    __tablename__ = "transcriptbioentity"

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))

    #Relationships
    locus = relationship(Locus, uselist=False, foreign_keys=[locus_id])

    __mapper_args__ = {'polymorphic_identity': 'TRANSCRIPT', 'inherit_condition': id == Bioentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status',
                     'description',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'locus']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        locus = obj_json.get('locus')
        if locus is not None:
            self.display_name = None if locus is None else locus.display_name + 't'
            self.format_name = None if locus is None else locus.format_name + 'T'
            self.link = None if locus is None else '/locus/' + locus.sgdid + '/overview'
            self.bioent_status = None if locus is None else locus.bioent_status
            self.description = None if locus is None else locus.description

class Complex(Bioentity):
    __tablename__ = 'complexbioentity'

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key = True)
    go_id = Column('go_id', Integer, ForeignKey(Go.id))
    cellular_localization = Column('cellular_localization', String)

    #Relationships
    go = relationship(Go, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "COMPLEX", 'inherit_condition': id==Bioentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status',
                     'description',
                     'cellular_localization',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'go']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        go = obj_json.get('go')
        if go is not None:
            self.display_name = go.display_name
            self.format_name = create_format_name(go.display_name.lower())
            self.link = '/complex/' + self.format_name + '/overview'
            self.description = go.description

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['subcomplexes'] = [x.child.to_min_json() for x in self.children]
        return obj_json