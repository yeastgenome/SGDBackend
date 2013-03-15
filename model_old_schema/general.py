'''
Created on Mar 14, 2013

@author: kpaskov
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from model_old_schema.go import GoRef
from model_old_schema.reference import Reference
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Dbxref(Base, EqualityByIDMixin):
    __tablename__ = 'dbxref'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('dbxref_no', Integer, primary_key = True)
    source = Column('source', String)
    dbxref_type = Column('dbxref_type', String)
    dbxref_id = Column('dbxref_id', String)
    dbxref_name = Column('dbxref_name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

class DbxrefRef(Base, EqualityByIDMixin):
    __tablename__ = 'dbxref_ref'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('dbxref_ref_no', Integer, primary_key = True)
    dbxref_id = Column('dbxref_no', Integer, ForeignKey('bud.dbxref.dbxref_no'))
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    
    dbxref = relationship(Dbxref, uselist=False)
    reference = relationship(Reference, uselist=False, backref= 'dbxrefrefs')
    
class GorefDbxref(Base, EqualityByIDMixin):
    __tablename__ = 'goref_dbxref'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('goref_dbxref_no', Integer, primary_key = True)
    go_ref_id = Column('go_ref_no', Integer, ForeignKey('bud.go_ref.go_ref_no'))
    dbxref_id = Column('dbxref_no', Integer, ForeignKey('bud.dbxref.dbxref_no'))
    support_type = Column('support_type', String)
    
    dbxref = relationship(Dbxref, uselist=False)
    go_ref = relationship(GoRef, uselist=False, backref='goref_dbxrefs')
