from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base
from feature import Feature
from general import Dbxref
from reference import Reference


__author__ = 'kpaskov'

class GoSynonym(Base, EqualityByIDMixin):
    __tablename__ = 'go_synonym'

    #Values
    id = Column('go_synonym_no', Integer, primary_key=True)
    name = Column('go_synonym', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

class Go(Base, EqualityByIDMixin):
    __tablename__ = 'go'

    id = Column('go_no', Integer, primary_key = True)
    go_go_id = Column('goid', Integer)
    go_term = Column('go_term', String)
    go_aspect = Column('go_aspect', String)
    go_definition = Column('go_definition', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

class GoGoSynonym(Base, EqualityByIDMixin):
    __tablename__ = 'go_gosyn'

    #Values
    id = Column('go_gosyn_no', Integer, primary_key=True)
    go_id = Column('go_no', Integer, ForeignKey(Go.id))
    gosynonym_id = Column('go_synonym_no', Integer, ForeignKey(GoSynonym.id))

    #Relationships
    gosynonym = relationship(GoSynonym, uselist=False, backref='go_gosynonyms')
    go = relationship(Go, uselist=False, backref='go_gosynonyms')
    
class GoFeature(Base, EqualityByIDMixin):
    __tablename__ = 'go_annotation'

    id = Column('go_annotation_no', Integer, primary_key=True)
    go_id = Column('go_no', Integer, ForeignKey(Go.id))
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    go_evidence = Column('go_evidence', String)
    annotation_type = Column('annotation_type', String)
    source = Column('source', String)
    date_last_reviewed = Column('date_last_reviewed', Date)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    go = relationship(Go, uselist=False)
    feature = relationship(Feature, uselist=False)
    
class GoRef(Base, EqualityByIDMixin):
    __tablename__ = 'go_ref'

    #Values
    id = Column('go_ref_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    go_annotation_id = Column('go_annotation_no', Integer, ForeignKey(GoFeature.id))
    has_qualifier = Column('has_qualifier', String)
    has_supporting_evidence = Column('has_supporting_evidence', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    reference = relationship(Reference, uselist=False)
    go_annotation = relationship(GoFeature, uselist=False, backref='go_refs')
    
    qualifier = association_proxy('go_qualifier', 'qualifier')
    
class GoQualifier(Base, EqualityByIDMixin):
    __tablename__ = 'go_qualifier'

    #Values
    id = Column('go_qualifier_no', Integer, primary_key = True)
    go_ref_id = Column('go_ref_no', Integer, ForeignKey(GoRef.id))
    qualifier = Column('qualifier', String)
    
    #Relationships
    go_ref = relationship(GoRef, uselist=False, backref=backref('go_qualifier', uselist=False))
    
class GoPath(Base, EqualityByIDMixin):
    __tablename__ = 'go_path'

    #Values
    id = Column('go_path_no', Integer, primary_key = True)
    ancestor_id = Column('ancestor_go_no', Integer, ForeignKey(Go.id))
    child_id = Column('child_go_no', Integer, ForeignKey(Go.id))
    generation = Column('generation', Integer)
    relationship_type = Column('relationship_type', String)
    ancestor_path = Column('ancestor_path', String)
    
    child = relationship(Go, uselist=False, foreign_keys=[child_id])
    ancestor = relationship(Go, uselist=False, foreign_keys=[ancestor_id])
   
class GorefDbxref(Base, EqualityByIDMixin):
    __tablename__ = 'goref_dbxref'

    id = Column('goref_dbxref_no', Integer, primary_key=True)
    goref_id = Column('go_ref_no', Integer, ForeignKey(GoRef.id))
    dbxref_id = Column('dbxref_no', Integer, ForeignKey(Dbxref.id))
    support_type = Column('support_type', String)
    
    dbxref = relationship(Dbxref, uselist=False)
    goref = relationship(GoRef, backref='goref_dbxrefs', uselist=False)
    
class GoSet(Base, EqualityByIDMixin):
    __tablename__ = 'go_set'

    #Values
    id = Column('go_set_no', Integer, primary_key = True)
    go_id = Column('go_no', Integer, ForeignKey(Go.id))
    name = Column('go_set_name', String)
    genome_count = Column('genome_count', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

    go = relationship(Go, uselist=False)


    

