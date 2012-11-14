'''
Created on Oct 24, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Feature module of the database schema.
'''
from model_old_schema import Base
from model_old_schema.config import SCHEMA
from model_old_schema.sequence import Sequence
from model_old_schema.taxonomy import Taxonomy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer, String

class Alias(Base):
    __tablename__ = 'alias'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('alias_no', Integer, primary_key = True)
    name = Column('alias_name', String)
    type = Column('alias_type', String)
    
    def __repr__(self):
        data = self.name
        return 'Alias(name=%s)' % data
    
class Feature(Base):
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
    sequences = relationship(Sequence)

    aliases = relationship("Alias", 
                           Table('feat_alias', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    
    def __repr__(self):
        data = self.name, self.gene_name
        return 'Feature(name=%s, gene_name=%s)' % data    
    
class Annotation(Base):
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

