'''
Created on May 23, 2013

@author: kpaskov
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from model_old_schema.feature import Feature
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date

#class Url(Base, EqualityByIDMixin):
#    __tablename__ = 'url'
#    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
#
#    id = Column('url_no', Integer, primary_key = True)
#    source = Column('source', String)
#    url_type = Column('url_type', String)
#    url = Column('url', String)
#    substitution_value = Column('substitution_value', String)
#    date_created = Column('date_created', Date)
#    created_by = Column('created_by', String)
    


class Dbxref(Base, EqualityByIDMixin):
    __tablename__ = 'dbxref'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('dbxref_no', Integer, primary_key = True)
    source = Column('source', String)
    dbxref_type = Column('dbxref_type', String)
    dbxref_id = Column('dbxref_id', String)
    name = Column('dbxref_name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
        
    #relationships
    feature_ids = association_proxy('dbxref_feats', 'feature_id')
    #urls = relationship(Url, secondary= Table('dbxref_url', Base.metadata, 
    #                                                Column('url_no', Integer, ForeignKey(Url.id)),
    #                                                Column('dbxref_no', Integer, ForeignKey('bud.dbxref.dbxref_no')),
    #                                                schema=SCHEMA))
    
class DbxrefFeat(Base, EqualityByIDMixin):
    __tablename__ = 'dbxref_feat'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('dbxref_feat_no', Integer, primary_key = True)
    dbxref_id = Column('dbxref_no', Integer, ForeignKey(Dbxref.id))
    feature_id = Column('feature_no', Integer)
    
    dbxref = relationship(Dbxref, backref='dbxref_feats', uselist=False)


    


    