from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base
from feature import Feature


__author__ = 'kpaskov'

class Dbxref(Base, EqualityByIDMixin):
    __tablename__ = 'dbxref'

    id = Column('dbxref_no', Integer, primary_key = True)
    source = Column('source', String)
    dbxref_type = Column('dbxref_type', String)
    dbxref_id = Column('dbxref_id', String)
    dbxref_name = Column('dbxref_name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    urls = association_proxy('dbxref_urls', 'url')

class Url(Base, EqualityByIDMixin):
    __tablename__ = 'url'

    id = Column('url_no', Integer, primary_key = True)
    source = Column('source', String)
    url_type = Column('url_type', String)
    url = Column('url', String)
    substitution_value = Column('substitution_value', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    features = association_proxy('feat_urls', 'feature')
    
class WebDisplay(Base, EqualityByIDMixin):
    __tablename__ = 'web_display'

    id = Column('web_display_no', Integer, primary_key = True)
    url_id = Column('url_no', Integer, ForeignKey(Url.id))
    web_page_name = Column('web_page_name', String)
    label_location = Column('label_location', String)
    label_type = Column('label_type', String)
    label_name = Column('label_name', String)
    is_default = Column('is_default', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    url = relationship(Url, uselist=False, backref='displays')
    
class FeatUrl(Base, EqualityByIDMixin):
    __tablename__ = 'feat_url'

    #Values
    id = Column('feat_url_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    url_id = Column('url_no', Integer, ForeignKey(Url.id))
    
    #Relationships
    feature = relationship(Feature, uselist=False, backref='feat_urls')
    url = relationship(Url, uselist=False, backref ='feat_urls')
    
class DbxrefFeat(Base, EqualityByIDMixin):
    __tablename__ = 'dbxref_feat'

    #Values
    id = Column('dbxref_feat_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    dbxref_id = Column('dbxref_no', Integer, ForeignKey(Dbxref.id))
    
    #Relationships
    feature = relationship(Feature, uselist=False)
    dbxref = relationship(Dbxref, uselist=False)
    
class DbxrefUrl(Base, EqualityByIDMixin):
    __tablename__ = 'dbxref_url'

    #Values
    id = Column('dbxref_url_no', Integer, primary_key = True)
    url_no = Column('url_no', Integer, ForeignKey(Url.id))
    dbxref_id = Column('dbxref_no', Integer, ForeignKey(Dbxref.id))
    
    #Relationships
    url = relationship(Url, uselist=False)
    dbxref = relationship(Dbxref, uselist=False, backref='dbxref_urls')
    
    
    
