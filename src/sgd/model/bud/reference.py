from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base
from feature import Feature
from general import Dbxref, Url


class Book(Base, EqualityByIDMixin):
    __tablename__ = 'book'

    id = Column('book_no', Integer, primary_key = True)
    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __repr__(self):
        data = self.title, self.total_pages, self.publisher
        return 'Book(title=%s, total_pages=%s, publisher=%s)' % data

class Journal(Base, EqualityByIDMixin):
    __tablename__ = 'journal'

    id = Column('journal_no', Integer, primary_key = True)
    full_name = Column('full_name', String)
    abbreviation = Column('abbreviation', String)
    issn = Column('issn', String)
    essn = Column('essn', String)
    publisher = Column('publisher', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __repr__(self):
        data = self.full_name, self.publisher
        return 'Journal(full_name=%s, publisher=%s)' % data

class Reference(Base, EqualityByIDMixin):
    __tablename__ = 'reference'

    id = Column('reference_no', Integer, primary_key = True)
    source = Column('source', String)
    status = Column('status', String)
    pdf_status = Column('pdf_status', String)
    dbxref_id = Column('dbxref_id', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    pubmed_id = Column('pubmed', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', String)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_no', Integer, ForeignKey(Journal.id))
    book_id = Column('book_no', Integer, ForeignKey(Book.id))
    doi = Column('doi', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    journal = relationship('Journal', uselist=False)
    book = relationship('Book', uselist=False)
    abst = relationship("Abstract", cascade='all,delete', uselist=False, backref='reference')
    abstract = association_proxy('abst', 'text')
    features = relationship(Feature, secondary= Table('ref_curation', Base.metadata, autoload=True, schema=Base.schema, extend_existing=True))
    author_references = relationship('AuthorReference', cascade='all,delete', 
                             backref=backref('reference'),
                            collection_class=attribute_mapped_collection('order'))
    reftype_references = relationship('RefReftype', cascade='all,delete',
                            collection_class=attribute_mapped_collection('id'), backref='reference')
    litGuides = relationship("LitGuide", cascade='all,delete')
    curations = relationship('RefCuration', cascade='all,delete')
    dbxrefs = association_proxy('dbxrefrefs', 'dbxref')

    def __repr__(self):
        data = self.title, self.pubmed_id
        return 'Reference(title=%s, pubmed_id=%s)' % data
    
class DbxrefRef(Base, EqualityByIDMixin):
    __tablename__ = 'dbxref_ref'

    id = Column('dbxref_ref_no', Integer, primary_key = True)
    dbxref_id = Column('dbxref_no', Integer, ForeignKey(Dbxref.id))
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    
    dbxref = relationship(Dbxref, uselist=False, lazy='joined')
    reference = relationship(Reference, uselist=False, backref='dbxrefrefs')

class Ref_URL(Base):
    __tablename__ = 'ref_url'

    id = Column('ref_url_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    url_id = Column('url_no', Integer, ForeignKey(Url.id))

    url = relationship(Url, uselist=False)
    reference = relationship(Reference, uselist=False)
    
class RefTemp(Base, EqualityByIDMixin):
    __tablename__ = 'ref_temp'

    id = Column('ref_temp_no', Integer, primary_key = True)
    pubmed_id = Column('pubmed', Integer)
    citation = Column('citation', String)
    fulltext_url = Column('fulltext_url', String)
    abstract = Column('abstract', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __repr__(self):
        data = self.pubmed_id
        return 'RefTemp(pubmed_id=%s)' % data
    
class RefBad(Base, EqualityByIDMixin):
    __tablename__ = 'ref_bad'

    pubmed_id = Column('pubmed', Integer, primary_key = True)
    dbxref_id = Column('dbxref_id', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __repr__(self):
        data = self.pubmed_id, self.dbxref_id
        return 'RefBad(pubmed_id=%s, dbxref_id=%s)' % data  
    
class Author(Base, EqualityByIDMixin):
    __tablename__ = 'author'

    id = Column('author_no', Integer, primary_key = True)
    name = Column('author_name', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __repr__(self):
        data = self.name
        return 'Author(name=%s)' % data   
    
class AuthorReference(Base, EqualityByIDMixin):
    __tablename__ = 'author_editor'

    id = Column('author_editor_no', Integer, primary_key = True)
    author_id = Column('author_no', Integer, ForeignKey(Author.id))
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    order = Column('author_order', Integer)
    type = Column('author_type', String)

    author = relationship('Author') 
    author_name = association_proxy('author', 'name')
    
class Abstract(Base, EqualityByIDMixin):
    __tablename__ = 'abstract'

    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id), primary_key=True)
    text = Column('abstract', String)

    def __repr__(self):
        data = self.text
        return 'Abstract(text=%s)' % data  
    
class RefType(Base, EqualityByIDMixin):
    __tablename__ = 'ref_type'

    id = Column('ref_type_no', Integer, primary_key = True)
    source = Column('source', String)
    name = Column('ref_type', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __repr__(self):
        data = self.name
        return 'RefType(name=%s)' % data    
    
class LitGuide(Base, EqualityByIDMixin):
    __tablename__ = 'lit_guide'

    id = Column('lit_guide_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    topic = Column('literature_topic', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    features = relationship("Feature", secondary= Table('litguide_feat', Base.metadata, autoload=True, schema=Base.schema, extend_existing=True))
    feature_ids = association_proxy('features', 'id')

    def __repr__(self):
        data = self.topic, self.reference_id, self.features
        return 'LitGuide(topic=%s, reference_id=%s, features=%s)' % data  
    
class RefCuration(Base, EqualityByIDMixin):
    __tablename__ = 'ref_curation'

    id = Column('ref_curation_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    task = Column('curation_task', String)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    comment = Column('curator_comment', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    feature = relationship(Feature, uselist=False)

    def __repr__(self):
        if self.feature_id is not None:
            data = self.task, self.feature, self.comment
            return 'RefCuration(task=%s, feature=%s, comment=%s)' % data
        else:
            data = self.task, self.comment
            return 'RefCuration(task=%s, feature=None, comment=%s)' % data 
    
class RefReftype(Base, EqualityByIDMixin):
    __tablename__ = 'ref_reftype'
    
    id = Column('ref_reftype_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    reftype_id = Column('ref_type_no', Integer, ForeignKey(RefType.id))

    reftype = relationship('RefType') 
    reftype_name = association_proxy('reftype', 'name')
    reftype_source = association_proxy('reftype', 'source')
    
class Reflink(Base):
    __tablename__ = 'ref_link'
    
    id = Column('ref_link_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    tab_name = Column('tab_name', String)
    primary_key = Column('primary_key', String)
    col_name = Column('col_name', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
class RefRelation(Base):
    __tablename__ = 'ref_relationship'
    
    id = Column('ref_relationship_no', Integer, primary_key=True)
    parent_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    child_id = Column('related_ref_no', Integer, ForeignKey(Reference.id))
    description = Column('description', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    #Relationships
    parent = relationship(Reference, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Reference, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    
class Litguide(Base):
    __tablename__ = 'lit_guide'
    
    id = Column('lit_guide_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    topic = Column('literature_topic', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

class LitguideFeat(Base):
    __tablename__ = 'litguide_feat'
    
    id = Column('litguide_feat_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    litguide_id = Column('lit_guide_no', Integer, ForeignKey(Litguide.id))
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    litguide = relationship(Litguide, uselist=False, backref='litguide_features')
    feature = relationship(Feature, uselist=False)
    topic = association_proxy('litguide', 'topic')
