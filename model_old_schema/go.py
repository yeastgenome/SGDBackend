'''
Created on Mar 5, 2013

@author: kpaskov
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from model_old_schema.feature import Feature
from model_old_schema.reference import Reference
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date


class GoSynonym(Base, EqualityByIDMixin):
    __tablename__ = 'go_synonym'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    #Values
    id = Column('go_synonym_no', Integer, primary_key=True)
    go_synonym = Column('go_synonym', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
class Go(Base, EqualityByIDMixin):
    __tablename__ = 'go'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('go_no', Integer, primary_key = True)
    go_go_id = Column('goid', Integer)
    go_term = Column('go_term', String)
    go_aspect = Column('go_aspect', String)
    go_definition = Column('go_definition', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #relationships
    synonyms = relationship(GoSynonym, secondary= Table('go_gosyn', Base.metadata, 
                                                        Column('go_no', Integer, ForeignKey('bud.go.go_no')),
                                                        Column('go_synonym_no', Integer, ForeignKey('bud.go_synonym.go_synonym_no')),
                                                        schema=SCHEMA), lazy='joined')
    
class GoFeature(Base, EqualityByIDMixin):
    __tablename__ = 'go_annotation'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('go_annotation_no', Integer, primary_key=True)
    go_id = Column('go_no', Integer, ForeignKey('bud.go.go_no'))
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    go_evidence = Column('go_evidence', String)
    annotation_type = Column('annotation_type', String)
    source = Column('source', String)
    date_last_reviewed = Column('date_last_reviewed', Date)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    go = relationship(Go, uselist=False, lazy='joined')
    feature = relationship(Feature, uselist=False)
    
class GoRef(Base, EqualityByIDMixin):
    __tablename__ = 'go_ref'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    #Values
    id = Column('go_ref_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    go_annotation_id = Column('go_annotation_no', Integer, ForeignKey('bud.go_annotation.go_annotation_no'))
    has_qualifier = Column('has_qualifier', String)
    has_supporting_evidence = Column('has_supporting_evidence', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    reference = relationship(Reference, uselist=False)
    go_annotation = relationship(GoFeature, uselist=False, backref=backref('go_refs', lazy='joined'))
    
    qualifier = association_proxy('go_qualifier', 'qualifier')
    
class GoQualifier(Base, EqualityByIDMixin):
    __tablename__ = 'go_qualifier'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    #Values
    id = Column('go_qualifier_no', Integer, primary_key = True)
    go_ref_id = Column('go_ref_no', Integer, ForeignKey('bud.go_ref.go_ref_no'))
    qualifier = Column('qualifier', String)
    
    #Relationships
    go_ref = relationship(GoRef, uselist=False, backref=backref('go_qualifier', uselist=False, lazy='joined'))
    
class GoPath(Base, EqualityByIDMixin):
    __tablename__ = 'go_path'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    #Values
    id = Column('go_path_no', Integer, primary_key = True)
    ancestor_id = Column('ancestor_go_no', Integer, ForeignKey('bud.go.go_no'))
    child_id = Column('child_go_no', Integer, ForeignKey('bud.go.go_no'))
    generation = Column('generation', Integer)
    relationship_type = Column('relationship_type', String)
    ancestor_path = Column('ancestor_path', String)
    
    child = relationship(Go, uselist=False, primaryjoin="GoPath.child_id==Go.id")
    ancestor = relationship(Go, uselist=False, primaryjoin="GoPath.ancestor_id==Go.id")
   

    
    
    
    
    

