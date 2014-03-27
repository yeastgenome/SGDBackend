from sqlalchemy import ForeignKey, CLOB
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, FetchedValue
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name
from src.sgd.model.nex.misc import Source, Relation, Strain


__author__ = 'kpaskov'

class Bioitem(Base, EqualityByIDMixin):
    __tablename__ = 'bioitem'
    
    id = Column('bioitem_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    bioitem_type = Column('bioitem_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    
    __mapper_args__ = {'polymorphic_on': class_type}
    
    def __init__(self, display_name, format_name, class_type, link, source, description, bioitem_type, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.description = description
        self.bioitem_type = bioitem_type
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.class_type)

    def to_json(self):
        return {
            'format_name': self.format_name,
            'display_name': self.display_name,
            'link': self.link,
            'id': self.id,
            'class_type': self.class_type,
            'bioitem_type': self.bioitem_type
            }

class Bioitemrelation(Relation):
    __tablename__ = 'bioitemrelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioitem.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioitem.id))

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM',
                       'inherit_condition': id == Relation.id}

    def __init__(self, source, relation_type, parent, child, date_created, created_by):
        Relation.__init__(self,
                          child.display_name + ' ' + ('' if relation_type is None else relation_type + ' ') + parent.display_name,
                          str(parent.id) + '_' + str(child.id),
                          'BIOITEM', source, relation_type, date_created, created_by)
        self.parent_id = parent.id
        self.child_id = child.id

class Domain(Bioitem):
    __tablename__ = "domainbioitem"
    
    id = Column('bioitem_id', Integer, primary_key=True)
    interpro_id = Column('interpro_id', String)
    interpro_description = Column('interpro_description', String)
    external_link = Column('external_url', String)
    
    __mapper_args__ = {'polymorphic_identity': 'DOMAIN',
                       'inherit_condition': id == Bioitem.id}
    
    def __init__(self, display_name, source, description, bioitem_type,
                 interpro_id, interpro_description, external_link):
        format_name = create_format_name(display_name)
        Bioitem.__init__(self, display_name, format_name, 'DOMAIN', '/domain/' + format_name + '/overview', source, description, bioitem_type, None, None)
        self.interpro_id = interpro_id
        self.interpro_description = interpro_description
        self.external_link = external_link

    def to_full_json(self):
        obj_json = self.to_json()
        obj_json['interpro_description'] = self.interpro_description
        obj_json['description'] = self.description
        obj_json['source'] = self.source.to_json()
        obj_json['external_link'] = self.external_link
        obj_json['interpro_id'] = self.interpro_id
        return obj_json

class Chemical(Bioitem):
    __tablename__ = "chemicalbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    chebi_id = Column('chebi_id', String)

    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL',
                       'inherit_condition': id == Bioitem.id}

    def __init__(self, display_name, source, chebi_id, description, date_created, created_by):
        format_name = create_format_name(display_name.lower())[:95]
        Bioitem.__init__(self, display_name, format_name, 'CHEMICAL', '/chemical/' + format_name + '/overview', source, description, None, date_created, created_by)
        self.format_name = create_format_name(display_name.lower())[:95]
        self.chebi_id = chebi_id

    def to_full_json(self):
        obj_json = self.to_json()
        obj_json['chebi_id'] = self.chebi_id
        obj_json['description'] = self.description
        return obj_json

class Contig(Bioitem):
    __tablename__ = "contigbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    residues = Column('residues', CLOB)
    strain_id = Column('strain_id', ForeignKey(Strain.id))

    #Relationships
    strain = relationship(Strain, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "CONTIG",
                       'inherit_condition': id==Bioitem.id}

    def __init__(self, display_name, source, residues, strain):
        format_name = strain.format_name + '_' + display_name
        Bioitem.__init__(self, display_name, format_name, 'CONTIG', '/contig/' + format_name + '/overview', source, None, None, None, None)
        self.residues = residues
        self.strain_id = strain.id

    def to_json(self):
        obj_json = Bioitem.to_json(self)
        obj_json['strain'] = self.strain.to_json()
        return obj_json

    def to_full_json(self):
        obj_json = self.to_json()
        obj_json['residues'] = self.residues
        return obj_json

class Allele(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'ALLELE',
                       'inherit_condition': id == Bioitem.id}

    def __init__(self, display_name, source, description):
        Bioitem.__init__(self, display_name, create_format_name(display_name), 'ALLELE', None, source, description, None, None, None)

class Orphanbioitem(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'ORPHAN',
                       'inherit_condition': id == Bioitem.id}

    def __init__(self, display_name, link, source, description, bioitem_type):
        Bioitem.__init__(self, display_name, create_format_name(display_name), 'ORPHAN', link, source, description, bioitem_type, None, None)

