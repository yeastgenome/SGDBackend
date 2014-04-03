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
    source = relationship(Source, uselist=False)
    
    __mapper_args__ = {'polymorphic_on': class_type}
    __eq_values__ = ['display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status', 'description']
    __eq_fks__ = ['source']
    
    def __init__(self, bioentity_id, display_name, format_name, class_type, link, source, sgdid, uniprotid,
                 bioent_status, description, date_created, created_by):
        self.id = bioentity_id
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = None if source is None else source.id
        self.sgdid = sgdid
        self.uniprotid = uniprotid
        self.bioent_status = bioent_status
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
            
    def unique_key(self):
        return self.format_name, self.class_type

    def to_json(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'format_name': self.format_name,
            'class_type': self.class_type,
            'link': self.link,
            'source': {'id': self.source_id} if self.source is None else self.source.to_json(),
            'sgdid': self.sgdid,
            'uniprotid': self.uniprotid,
            'bioent_status': self.bioent_status,
            'description': self.description,
            'aliases': [x.to_json() for x in self.aliases]
        }

    def to_min_json(self):
        obj_json = UpdateByJsonMixin.to_min_json(self)
        obj_json['class_type'] = self.class_type
        return obj_json

    @classmethod
    def from_json(cls, obj_json):
        obj = cls(obj_json.get('id'), obj_json.get('display_name'), obj_json.get('format_name'),
                  obj_json.get('class_type'), obj_json.get('link'), None, obj_json.get('sgdid'),
                  obj_json.get('uniprotid'), obj_json.get('bioent_status'), obj_json.get('description'),
                  obj_json.get('date_created'), obj_json.get('created_by'))
        obj.source_id = None if 'source' not in obj_json else obj_json['source']['id']
        return obj
    
class Bioentityurl(Url):
    __tablename__ = 'bioentityurl'
    
    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    subclass_type = Column('subclass', String)
    
    bioentity = relationship(Bioentity, uselist=False, backref=backref('urls', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Url.id}
    
    def __init__(self, display_name, link, source, category, bioentity, date_created, created_by):
        Url.__init__(self, display_name, bioentity.format_name, 'BIOENTITY', link, source, category, 
                     date_created, created_by)
        self.bioentity_id = bioentity.id
        self.subclass_type = bioentity.class_type
    
class Bioentityalias(Alias):
    __tablename__ = 'bioentityalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    subclass_type = Column('subclass', String)
    is_external_id = Column('is_external_id', Integer)

    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, link, source, category, bioentity, is_external_id, date_created, created_by):
        Alias.__init__(self, display_name, str(bioentity.id), 'BIOENTITY', link, source, category, date_created,
                       created_by)
        self.bioentity_id = bioentity.id
        self.subclass_type = bioentity.class_type
        self.is_external_id = is_external_id

class Bioentityrelation(Relation):
    __tablename__ = 'bioentityrelation'

    id = Column('relation_id', Integer, ForeignKey(Relation.id), primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioentity.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioentity.id))
    subclass_type = Column('subclass', String)
    
    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Relation.id}
   
    #Relationships
    parent = relationship(Bioentity, backref=backref("children", passive_deletes=True), uselist=False,
                          primaryjoin="Bioentityrelation.parent_id==Bioentity.id")
    child = relationship(Bioentity, backref=backref("parents", passive_deletes=True), uselist=False,
                         primaryjoin="Bioentityrelation.child_id==Bioentity.id")

    def __init__(self, source, relation_type, parent, child, date_created, created_by):
        Relation.__init__(self, str(parent.id )+ '-' + str(child.id), str(parent.id )+ '-' + str(child.id), 'BIOENTITY', source,
                          relation_type, date_created, created_by)
        self.parent_id = parent.id
        self.child_id = child.id
        self.subclass_type = parent.class_type
                       
class Locus(Bioentity):
    __tablename__ = "locusbioentity"
    
    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    locus_type = Column('locus_type', String)
    gene_name = Column('gene_name', String)
        
    __mapper_args__ = {'polymorphic_identity': 'LOCUS', 'inherit_condition': id == Bioentity.id}
    __eq_values__ = ['display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status', 'description',
                     'name_description', 'headline', 'locus_type', 'gene_name']
    __eq_fks__ = ['source']

    def __init__(self, bioentity_id, display_name, format_name, source, sgdid, uniprotid, bioent_status, 
                 locus_type, name_description, headline, description, gene_name,
                 date_created, created_by):
        Bioentity.__init__(self, bioentity_id, display_name, format_name, 'LOCUS', '/cgi-bin/locus.fpl?locus=' + sgdid,
                           source, sgdid, uniprotid, bioent_status, description, date_created, created_by)
        self.name_description = name_description
        self.headline = headline
        self.locus_type = locus_type
        self.gene_name = gene_name

    def to_json(self):
        obj_json = Bioentity.to_json(self)
        obj_json['locus_type'] = self.locus_type
        obj_json['name_description'] = self.name_description
        obj_json['headline'] = self.headline
        obj_json['gene_name'] = self.gene_name
        return obj_json

    @classmethod
    def from_json(cls, obj_json):
        obj = cls(obj_json.get('id'), obj_json.get('display_name'), obj_json.get('format_name'),
                    None, obj_json.get('sgdid'), obj_json.get('uniprotid'), obj_json.get('bioent_status'),
                    obj_json.get('locus_type'), obj_json.get('name_description'), obj_json.get('headline'),
                    obj_json.get('description'), obj_json.get('gene_name'), obj_json.get('date_created'),
                    obj_json.get('created_by'))
        obj.source_id = None if 'source' not in obj_json else obj_json['source']['id']
        return obj
    
class Protein(Bioentity):
    __tablename__ = "proteinbioentity"

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))

    locus = relationship(Locus, uselist=False, primaryjoin="Protein.locus_id==Locus.id")

    __mapper_args__ = {'polymorphic_identity': 'PROTEIN', 'inherit_condition': id == Bioentity.id}
    __eq_values__ = ['display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status', 'description']
    __eq_fks__ = ['source', 'locus']

    def __init__(self, bioentity_id, source, locus, date_created, created_by):
        display_name = None if locus is None else locus.display_name + 't'
        format_name = None if locus is None else locus.format_name + 'T'
        link = None if locus is None else '/locus/' + locus.sgdid + '/overview'
        bioent_status = None if locus is None else locus.bioent_status
        description = None if locus is None else locus.description
        Bioentity.__init__(self, bioentity_id, display_name, format_name, 'PROTEIN', link, source, None, None,
                           bioent_status, description, date_created, created_by)
        self.locus_id = None if locus is None else locus.id

    def to_json(self):
        obj_json = Bioentity.to_json(self)
        obj_json['locus'] = {'id': self.locus_id} if self.locus is None else self.locus.to_json()
        return obj_json

    @classmethod
    def from_json(cls, obj_json):
        obj = cls(obj_json.get('id'), None, None, obj_json.get('date_created'), obj_json.get('created_by'))
        obj.source_id = None if 'source' not in obj_json else obj_json['source']['id']
        obj.locus_id = None if 'locus' not in obj_json else obj_json['locus']['id']
        obj.display_name = obj_json.get('display_name')
        obj.format_name = obj_json.get('format_name')
        obj.link = obj_json.get('link')
        obj.bioent_status = obj_json.get('bioent_status')
        obj.description = obj_json.get('description')
        return obj

class Transcript(Bioentity):
    __tablename__ = "transcriptbioentity"

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))

    locus = relationship(Locus, uselist=False, primaryjoin="Transcript.locus_id==Locus.id")

    __mapper_args__ = {'polymorphic_identity': 'TRANSCRIPT', 'inherit_condition': id == Bioentity.id}
    __eq_values__ = ['display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status', 'description']
    __eq_fks__ = ['source', 'locus']

    def __init__(self, bioentity_id, source, locus, date_created, created_by):
        display_name = None if locus is None else locus.display_name + 't'
        format_name = None if locus is None else locus.format_name + 'T'
        link = None if locus is None else '/locus/' + locus.sgdid + '/overview'
        bioent_status = None if locus is None else locus.bioent_status
        description = None if locus is None else locus.description
        Bioentity.__init__(self, bioentity_id, display_name, format_name, 'TRANSCRIPT', link, source, None, None,
                           bioent_status, description, date_created, created_by)
        self.locus_id = None if locus is None else locus.id

    def to_json(self):
        obj_json = Bioentity.to_json(self)
        obj_json['locus'] = {'id': self.locus_id} if self.locus is None else self.locus.to_json()
        return obj_json

    @classmethod
    def from_json(cls, obj_json):
        obj = cls(obj_json.get('id'), None, None, obj_json.get('date_created'), obj_json.get('created_by'))
        obj.source_id = None if 'source' not in obj_json else obj_json['source']['id']
        obj.locus_id = None if 'locus' not in obj_json else obj_json['locus']['id']
        obj.display_name = obj_json.get('display_name')
        obj.format_name = obj_json.get('format_name')
        obj.link = obj_json.get('link')
        obj.bioent_status = obj_json.get('bioent_status')
        obj.description = obj_json.get('description')
        return obj

class Complex(Bioentity):
    __tablename__ = 'complexbioentity'

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key = True)
    go_id = Column('go_id', Integer, ForeignKey(Go.id))
    cellular_localization = Column('cellular_localization', String)

    #Relationships
    go = relationship(Go, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "COMPLEX", 'inherit_condition': id==Bioentity.id}
    __eq_values__ = ['display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status', 'description',
                     'cellular_localization']
    __eq_fks__ = ['source', 'go']

    def __init__(self, complex_id, source, sgdid,
                 go, cellular_localization, date_created=None, created_by=None):
        display_name = None if go is None else go.display_name
        format_name = None if go is None else create_format_name(go.display_name.lower())
        link = None if go is None else '/complex/' + format_name + '/overview'
        description = None if go is None else go.description
        Bioentity.__init__(self, complex_id, display_name, format_name, 'COMPLEX', link,
                           source, sgdid, None, None, description, date_created, created_by)
        self.go_id = None if go is None else go.id
        self.cellular_localization = cellular_localization

    def to_json(self):
        obj_json = Bioentity.to_json(self)
        obj_json['go'] = {'id': self.go_id} if self.go is None else self.go.to_min_json()
        obj_json['cellular_localization'] = self.cellular_localization
        obj_json['sgdid'] = self.sgdid
        obj_json['description'] = self.description
        obj_json['class_type'] = self.class_type
        obj_json['subcomplexes'] = [x.child.to_min_json() for x in self.children]
        return obj_json

    @classmethod
    def from_json(cls, obj_json):
        obj = cls(obj_json.get('id'), None, obj_json.get('sgdid'), None, obj_json.get('cellular_localization'),
                   obj_json.get('date_created'), obj_json.get('created_by'))
        obj.source_id = None if 'source' not in obj_json else obj_json['source']['id']
        obj.go_id = None if 'go' not in obj_json else obj_json['go']['id']
        obj.display_name = obj_json.get('display_name')
        obj.format_name = obj_json.get('format_name')
        obj.link = obj_json.get('link')
        obj.description = obj_json.get('description')
        return obj