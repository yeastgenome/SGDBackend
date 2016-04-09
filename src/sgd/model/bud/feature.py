from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base
from taxonomy import Taxonomy

__author__ = 'kpaskov'
    
class Feature(Base, EqualityByIDMixin):
    __tablename__ = 'feature'

    #Values
    id = Column('feature_no', Integer, primary_key = True)
    taxon_id = Column('taxon_id', Integer, ForeignKey(Taxonomy.id))
    dbxref_id = Column('dbxref_id', String)
    name = Column('feature_name', String)
    type = Column('feature_type', String)
    source = Column('source', String)
    status = Column('status', String)
    gene_name = Column('gene_name', String)
    
    #Relationships
    taxonomy = relationship(Taxonomy, uselist=False)

    aliases = relationship("AliasFeature", lazy='subquery')
    alias_names = association_proxy('aliases', 'alias_name')
    
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #phenotypes = relationship('Phenotype_Feature', lazy='joined')

    def __repr__(self):
        data = self.name, self.gene_name
        return 'Feature(name=%s, gene_name=%s)' % data

class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'

    id = Column('alias_no', Integer, primary_key = True)
    name = Column('alias_name', String)
    type = Column('alias_type', String)

    def __repr__(self):
        data = self.name
        return 'Alias(name=%s)' % data

class AliasFeature(Base, EqualityByIDMixin):
    __tablename__ = 'feat_alias'

    id = Column('feat_alias_no', Integer, primary_key=True)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    alias_id = Column('alias_no', Integer, ForeignKey(Alias.id))
    used_for_search = Column('used_for_search', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

    #Relationships
    alias = relationship('Alias')
    alias_name = association_proxy('alias', 'name')
    alias_type = association_proxy('alias', 'type')

class FeatCuration(Base, EqualityByIDMixin):
    __tablename__ = 'feat_curation'

    id = Column('feat_curation_no', Integer, primary_key = True)
    task = Column('curation_task', String)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    comment = Column('curator_comment', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __repr__(self):
        data = self.task, self.feature_id, self.comment
        return 'FeatCuration(task=%s, feature_id=%s, comment=%s)' % data

class Archive(Base, EqualityByIDMixin):
    __tablename__ = 'archive'

    id = Column('archive_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    archive_type = Column('archive_type', String)
    old_value = Column('old_value', String)
    new_value = Column('new_value', String)
    description = Column('description', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
class FeatRel(Base, EqualityByIDMixin):
    __tablename__ = 'feat_relationship'

    #Values
    id = Column('feat_relationship_no', Integer, primary_key = True)
    parent_id = Column('parent_feature_no', Integer, ForeignKey(Feature.id))
    child_id = Column('child_feature_no', Integer, ForeignKey(Feature.id))
    relationship_type = Column('relationship_type', String)
    rank = Column('rank', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

    #Relationships
    parent = relationship(Feature, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Feature, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    
class Annotation(Base, EqualityByIDMixin):
    __tablename__ = 'feat_annotation'

    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id), primary_key=True)
    qualifier = Column('qualifier', String)
    attribute = Column('feat_attribute', String)
    description = Column('description', String)
    headline = Column('headline', String)
    name_description = Column('name_description', String)
    genetic_position = Column('genetic_position', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

    feature = relationship(Feature, backref=backref('annotation', uselist=False))
    
    def __repr__(self):
        data = self.headline, self.qualifier
        return 'Annotation(headline=%s, qualifier=%s)' % data

class FeatureProperty(Base, EqualityByIDMixin):
    __tablename__ = 'feat_property'

    id = Column('feat_property_no', Integer, primary_key=True)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    source = Column('source', String)
    property_type = Column('property_type', String)
    property_value = Column('property_value', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

class GeneReservation(Base, EqualityByIDMixin):
    __tablename__ = 'gene_reservation'

    id = Column('feature_no', Integer, primary_key=True)
    reservation_date = Column('reservation_date', Date)
    expiration_date = Column('expiration_date', Date)
    reserved_gene_name = Column('reserved_gene_name', String)
    date_standardized = Column('date_standardized', Date)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
