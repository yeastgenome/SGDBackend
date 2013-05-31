'''
Created on Apr 22, 2013

@author: kpaskov
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class CVTerm(Base, EqualityByIDMixin):
    __tablename__ = 'cv_term'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('cv_term_no', Integer, primary_key = True)
    cv_no = Column('cv_no', Integer)
    name = Column('term_name', String)
    dbxref_id = Column('dbxref_id', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    definition = Column('cvterm_definition', String)
    
    parents = association_proxy('parent_rels', 'parent')
        
class CVTermRel(Base, EqualityByIDMixin):
    __tablename__ = 'cvterm_relationship'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('cvterm_relationship_no', Integer, primary_key = True)
    child_id = Column('child_cv_term_no', Integer, ForeignKey(CVTerm.id))
    parent_id = Column('parent_cv_term_no', Integer, ForeignKey(CVTerm.id))
    relationship_type = Column('relationship_type', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    child = relationship(CVTerm, uselist=False, primaryjoin="CVTermRel.child_id==CVTerm.id", backref='parent_rels')
    parent = relationship(CVTerm, uselist=False, primaryjoin="CVTermRel.parent_id==CVTerm.id")
                        