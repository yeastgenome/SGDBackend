__author__ = 'kpaskov'

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model.nex import create_format_name, Base
from src.sgd.model.nex.basic import BasicObject, UpdateByJsonMixin
from src.sgd.model.nex.misc import Relation


class Bioentity(BasicObject):
    __tablename__ = 'bioentity'

    id = Column('id', ForeignKey(BasicObject.id), Integer, primary_key=True)
    budid = Column('budid', Integer)
    sgdid = Column('sgdid', String)
    status = Column('status', String)

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == BasicObject.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'description', 'bud_id', 'status', 'date_created', 'created_by', 'class_type']
    __fks__ = ['source', 'urls', 'aliases', 'relations', 'qualities', 'tags', 'paragraphs']

    def unique_key(self):
        return self.class_type, self.format_name


class Locus(Bioentity):
    __tablename__ = "locus"

    id = Column('id', Integer, ForeignKey(BasicObject.id), primary_key=True)
    uniprotid = Column('uniprotid', String)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    locus_type = Column('locus_type', String)
    gene_name = Column('gene_name', String)
    qualifier = Column('qualifier', String)
    genetic_position = Column('genetic_position', Integer)

    __mapper_args__ = {'polymorphic_identity': 'LOCUS', 'inherit_condition': id == BasicObject.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'description', 'bud_id', 'status', 'date_created', 'created_by', 'class_type',
                     'uniprotid', 'name_description', 'headline', 'locus_type', 'gene_name', 'qualifier', 'genetic_position']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.link = None if self.sgdid is None else '/locus/' + self.sgdid + '/overview'


class LocusRelation(Relation):
    __tablename__ = 'locusrelation'

    id = Column('id', Integer, ForeignKey(Relation.id), primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Locus.id))
    child_id = Column('child_id', Integer, ForeignKey(Locus.id))

    #Relationships
    parent = relationship(Locus, backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Locus, backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    __mapper_args__ = {'polymorphic_identity': 'LOCUS', 'inherit_condition': id == Relation.id}


class Organism(Bioentity):
    __tablename__ = 'strain'

    id = Column('id', Integer, ForeignKey(BasicObject.id), primary_key=True)
    genotype = Column('genotype', String)

    __mapper_args__ = {'polymorphic_identity': 'STRAIN', 'inherit_condition': id == BasicObject.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'description', 'bud_id', 'status', 'date_created', 'created_by', 'class_type',
                'genotype']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name.replace('.', ''))
        self.link = None if self.format_name is None else '/strain/' + self.format_name + '/overview'


class OrganismRelation(Relation):
    __tablename__ = 'organismrelation'

    id = Column('id', Integer, ForeignKey(Relation.id), primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Organism.id))
    child_id = Column('child_id', Integer, ForeignKey(Organism.id))

    #Relationships
    parent = relationship(Organism, backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Organism, backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    __mapper_args__ = {'polymorphic_identity': 'ORGANISM', 'inherit_condition': id == Relation.id}