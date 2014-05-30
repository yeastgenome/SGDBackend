from sqlalchemy import ForeignKey, CLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin
from src.sgd.model.nex.misc import Source, Relation, Strain, Url, Alias

__author__ = 'kpaskov'

class Bioitem(Base, EqualityByIDMixin, UpdateByJsonMixin):
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
    source = relationship(Source, uselist=False, lazy='joined')
    
    __mapper_args__ = {'polymorphic_on': class_type, 'with_polymorphic':'*'}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def unique_key(self):
        return self.format_name, self.class_type

    def to_min_json(self):
        obj_json = UpdateByJsonMixin.to_min_json(self)
        obj_json['class_type'] = self.class_type
        return obj_json

class Bioitemrelation(Relation):
    __tablename__ = 'bioitemrelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioitem.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    parent = relationship(Bioitem, backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Bioitem, backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM', 'inherit_condition': id == Relation.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relation_type',
                     'parent_id', 'child_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))
        self.display_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))

class Bioitemurl(Url):
    __tablename__ = 'bioitemurl'

    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    bioitem = relationship(Bioitem, uselist=False, backref=backref('urls', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM', 'inherit_condition': id == Url.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioitem_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioitem_id'))

class Bioitemalias(Alias):
    __tablename__ = 'bioitemalias'

    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    bioitem = relationship(Bioitem, uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM', 'inherit_condition': id == Alias.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioitem_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioitem_id'))

class Domain(Bioitem):
    __tablename__ = "domainbioitem"
    
    id = Column('bioitem_id', Integer, primary_key=True)
    interpro_id = Column('interpro_id', String)
    interpro_description = Column('interpro_description', String)

    __mapper_args__ = {'polymorphic_identity': 'DOMAIN', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'interpro_id', 'interpro_description',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']
    
    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))
        self.link = None if self.format_name is None else '/domain/' + self.format_name + '/overview'

    @hybrid_property
    def count(self):
        return len(set([x.locus_id for x in self.domain_evidences]))

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        return obj_json

class Chemical(Bioitem):
    __tablename__ = "chemicalbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    chebi_id = Column('chebi_id', String)

    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'chebi_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))[:95]
        self.link = None if self.format_name is None else '/chemical/' + self.format_name + '/overview'

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        return obj_json


number_to_roman = {'01': 'I', '1': 'I',
                   '02': 'II', '2': 'II',
                   '03': 'III', '2': 'III',
                   '04': 'IV', '2': 'IV',
                   '05': 'V', '2': 'V',
                   '06': 'VI', '2': 'VI',
                   '07': 'VII', '2': 'VII',
                   '08': 'VIII', '2': 'VIII',
                   '09': 'IX', '2': 'IX',
                   '10': 'X', '2': 'X',
                   '11': 'XI', '2': 'XI',
                   '12': 'XII', '2': 'XII',
                   '13': 'XIII', '2': 'XIII',
                   '14': 'XIV', '2': 'XIV',
                   '15': 'XV', '2': 'XV',
                   '16': 'XVI', '2': 'XVI',
                   '17': 'XVII', '2': 'XVII'
                   }

class Contig(Bioitem):
    __tablename__ = "contigbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    residues = Column('residues', CLOB)
    strain_id = Column('strain_id', ForeignKey(Strain.id))

    #Relationships
    strain = relationship(Strain, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "CONTIG", 'inherit_condition': id==Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'residues',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'strain']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('strain') is None or obj_json.get('display_name') is None else obj_json.get('strain').format_name + '_' + obj_json.get('display_name')
        self.link = None if self.format_name is None else '/contig/' + self.format_name + '/overview'
        if self.display_name.startswith('chr'):
            self.display_name = 'Chromosome ' + (self.display_name[3:] if self.display_name[3:] not in number_to_roman else number_to_roman[self.display_name[3:]])

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        overview = {}
        for evidence in self.dnasequence_evidences:
            if evidence.locus.locus_type in overview:
                overview[evidence.locus.locus_type] += 1
            else:
                overview[evidence.locus.locus_type] = 1
        overview = [[key, value] for key, value in overview.iteritems()]
        overview.insert(0, ['Feature Type', 'Count'])
        obj_json['overview'] = overview

        return obj_json

class Allele(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'ALLELE', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))

class Orphanbioitem(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'ORPHAN', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))
