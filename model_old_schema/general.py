'''
Created on Mar 14, 2013

@author: kpaskov
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
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
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    
    dbxref = relationship(Dbxref, uselist=False, lazy='joined')
    reference = relationship(Reference, uselist=False, backref= 'dbxrefrefs')

class Url(Base, EqualityByIDMixin):
    __tablename__ = 'url'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('url_no', Integer, primary_key = True)
    source = Column('source', String)
    url_type = Column('url_type', String)
    url = Column('url', String)
    substitution_value = Column('substitution_value', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
