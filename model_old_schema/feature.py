'''
Created on Oct 24, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Feature module of the database schema.
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from model_old_schema.taxonomy import Taxonomy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('alias_no', Integer, primary_key = True)
    name = Column('alias_name', String)
    type = Column('alias_type', String)
    
    def __repr__(self):
        data = self.name
        return 'Alias(name=%s)' % data
    
class AliasFeature(Base, EqualityByIDMixin):
    __tablename__ = 'feat_alias'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('feat_alias_no', Integer, primary_key=True)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    alias_id = Column('alias_no', Integer, ForeignKey('bud.alias.alias_no'))
    used_for_search = Column('used_for_search', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    alias = relationship('Alias')
    alias_name = association_proxy('alias', 'name')
    alias_type = association_proxy('alias', 'type')
    
class Feature(Base, EqualityByIDMixin):
    __tablename__ = 'feature'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    #Values
    id = Column('feature_no', Integer, primary_key = True)
    taxon_id = Column('taxon_id', Integer, ForeignKey('bud.taxonomy.taxon_id'))
    dbxref_id = Column('dbxref_id', String)
    name = Column('feature_name', String)
    type = Column('feature_type', String)
    source = Column('source', String)
    status = Column('status', String)
    gene_name = Column('gene_name', String)
    
    #Relationships
    annotation = relationship('Annotation', uselist=False)
   
    taxonomy = relationship(Taxonomy, uselist=False)

    aliases = relationship("AliasFeature", lazy='subquery')
    alias_names = association_proxy('aliases', 'name')
    
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #phenotypes = relationship('Phenotype_Feature', lazy='joined')
    
    
    def __repr__(self):
        data = self.name, self.gene_name
        return 'Feature(name=%s, gene_name=%s)' % data    
    
class FeatRel(Base, EqualityByIDMixin):
    __tablename__ = 'feat_relationship'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    #Values
    id = Column('feat_relationship_no', Integer, primary_key = True)
    parent_id = Column('parent_feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    child_id = Column('child_feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    relationship_type = Column('relationship_type', String)
    rank = Column('rank', Integer)
    
class Annotation(Base, EqualityByIDMixin):
    __tablename__ = 'feat_annotation'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'), primary_key=True)
    qualifier = Column('qualifier', String)
    attribute = Column('feat_attribute', String)
    description = Column('description', String)
    headline = Column('headline', String)
    name_description = Column('name_description', String)
    genetic_position = Column('genetic_position', String)
    
    def __repr__(self):
        data = self.headline, self.qualifier
        return 'Annotation(headline=%s, qualifier=%s)' % data
    
    


