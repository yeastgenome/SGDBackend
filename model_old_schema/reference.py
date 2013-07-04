'''
Created on Nov 7, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Reference module of the database schema.
'''
from model_old_schema import Base, EqualityByIDMixin, UniqueMixin, SCHEMA
from model_old_schema.feature import Feature
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date
       
class Reference(Base, EqualityByIDMixin, UniqueMixin):
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
    journal_id = Column('journal_no', Integer, ForeignKey('bud.journal.journal_no'))
    book_id = Column('book_no', Integer, ForeignKey('bud.book.book_no'))
    doi = Column('doi', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    journal = relationship('Journal', uselist=False)
    book = relationship('Book', uselist=False)
    abst = relationship("Abstract", cascade='all,delete', uselist=False, backref='reference')
    abstract = association_proxy('abst', 'text')
    features = relationship(Feature, secondary= Table('ref_curation', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    author_references = relationship('AuthorReference', cascade='all,delete', 
                             backref=backref('reference'),
                            collection_class=attribute_mapped_collection('order'))
    reftype_references = relationship('RefReftype', cascade='all,delete',
                            collection_class=attribute_mapped_collection('id'), backref='reference')
    litGuides = relationship("LitGuide", cascade='all,delete')
    curations = relationship('RefCuration', cascade='all,delete')
    dbxrefs = association_proxy('dbxrefrefs', 'dbxref') 

        
    @classmethod
    def unique_hash(cls, pubmed_id):
        return pubmed_id

    @classmethod
    def unique_filter(cls, query, pubmed_id):
        return query.filter(Reference.pubmed_id == pubmed_id)

    def __repr__(self):
        data = self.title, self.pubmed_id
        return 'Reference(title=%s, pubmed_id=%s)' % data
    
class Book(Base, EqualityByIDMixin):
    __tablename__ = 'book'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

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
    
class Journal(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'journal'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('journal_no', Integer, primary_key = True)
    full_name = Column('full_name', String)
    abbreviation = Column('abbreviation', String)
    issn = Column('issn', String)
    essn = Column('essn', String)
    publisher = Column('publisher', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    @classmethod
    def unique_hash(cls, abbreviation):
        return abbreviation

    @classmethod
    def unique_filter(cls, query, abbreviation):
        return query.filter(Journal.abbreviation == abbreviation)

    def __repr__(self):
        data = self.full_name, self.publisher
        return 'Journal(full_name=%s, publisher=%s)' % data
    
class RefTemp(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_temp'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_temp_no', Integer, primary_key = True)
    pubmed_id = Column('pubmed', Integer)
    citation = Column('citation', String)
    fulltext_url = Column('fulltext_url', String)
    abstract = Column('abstract', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    @classmethod
    def unique_hash(cls, pubmed_id):
        return pubmed_id

    @classmethod
    def unique_filter(cls, query, pubmed_id):
        return query.filter(RefTemp.pubmed_id == pubmed_id)

    def __repr__(self):
        data = self.pubmed_id
        return 'RefTemp(pubmed_id=%s)' % data
    
class RefBad(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_bad'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    pubmed_id = Column('pubmed', Integer, primary_key = True)
    dbxref_id = Column('dbxref_id', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    @classmethod
    def unique_hash(cls, pubmed_id):
        return pubmed_id

    @classmethod
    def unique_filter(cls, query, pubmed_id):
        return query.filter(RefBad.pubmed_id == pubmed_id)

    def __repr__(self):
        data = self.pubmed_id, self.dbxref_id
        return 'RefBad(pubmed_id=%s, dbxref_id=%s)' % data  
    
class Author(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'author'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('author_no', Integer, primary_key = True)
    name = Column('author_name', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    @classmethod
    def unique_hash(cls, name):
        return name

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(Author.name == name)

    def __repr__(self):
        data = self.name
        return 'Author(name=%s)' % data   
    
class AuthorReference(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'author_editor'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('author_editor_no', Integer, primary_key = True)
    author_id = Column('author_no', Integer, ForeignKey('bud.author.author_no'))
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    order = Column('author_order', Integer)
    type = Column('author_type', String)
        
    @classmethod
    def unique_hash(cls, author, order, ar_type):
        return '%s_%s_%s_%s' % (author, order, ar_type)  

    @classmethod
    def unique_filter(cls, query, author, reference_id, order, ar_type):
        return query.filter(AuthorReference.order == order, AuthorReference.author == author, AuthorReference.ar_type == ar_type)
    
    author = relationship('Author') 
    author_name = association_proxy('author', 'name')
    
class Abstract(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'abstract'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'), primary_key = True)
    text = Column('abstract', String)

        
    @classmethod
    def unique_hash(cls, text, reference_id):
        return reference_id

    @classmethod
    def unique_filter(cls, query, text, reference_id):
        return query.filter(Abstract.reference_id == reference_id)

    def __repr__(self):
        data = self.text
        return 'Abstract(text=%s)' % data  
    
class RefType(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_type'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_type_no', Integer, primary_key = True)
    source = Column('source', String)
    name = Column('ref_type', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    @classmethod
    def unique_hash(cls, name):
        return name

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(RefType.name == name)

    def __repr__(self):
        data = self.name
        return 'RefType(name=%s)' % data    
    
class LitGuide(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'lit_guide'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('lit_guide_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey("bud.reference.reference_no"))
    topic = Column('literature_topic', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    features = relationship("Feature", secondary= Table('litguide_feat', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    feature_ids = association_proxy('features', 'id')
        
    @classmethod
    def unique_hash(cls, reference_id, topic):
        return '%s_%s' % (reference_id, topic)  

    @classmethod
    def unique_filter(cls, query, reference_id, topic):
        return query.filter(LitGuide.reference_id == reference_id, LitGuide.topic == topic)

    def __repr__(self):
        data = self.topic, self.reference_id, self.features
        return 'LitGuide(topic=%s, reference_id=%s, features=%s)' % data  
    
class RefCuration(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_curation'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_curation_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    task = Column('curation_task', String)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    comment = Column('curator_comment', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    feature = relationship('Feature', uselist=False)
        
    @classmethod
    def unique_hash(cls, reference_id, task, feature_id):
        return '%s_%s_%s' % (reference_id, task, feature_id)  

    @classmethod
    def unique_filter(cls, query, reference_id, task, feature_id):
        return query.filter(RefCuration.reference_id == reference_id, RefCuration.task == task, RefCuration.feature_id == feature_id)

    def __repr__(self):
        if self.feature_id is not None:
            data = self.task, self.feature, self.comment
            return 'RefCuration(task=%s, feature=%s, comment=%s)' % data
        else:
            data = self.task, self.comment
            return 'RefCuration(task=%s, feature=None, comment=%s)' % data 
    
class RefReftype(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_reftype'
    
    id = Column('ref_reftype_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    reftype_id = Column('ref_type_no', Integer, ForeignKey('bud.ref_type.ref_type_no'))
        
    @classmethod
    def unique_hash(cls, reference_id, reftype_id):
        return '%s_%s_%s_%s' % (reference_id, reftype_id)  

    @classmethod
    def unique_filter(cls, query, reference_id, reftype_id):
        return query.filter(RefReftype.reference_id == reference_id, RefReftype.reftype_id == reftype_id)
    
    reftype = relationship('RefType') 
    reftype_name = association_proxy('reftype', 'name')
    reftype_source = association_proxy('reftype', 'source')
    
class Reflink(Base):
    __tablename__ = 'ref_link'
    
    id = Column('ref_link_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    tab_name = Column('tab_name', String)
    primary_key = Column('primary_key', String)
    col_name = Column('col_name', String)
        
class RefRelation(Base):
    __tablename__ = 'ref_relationship'
    
    id = Column('ref_relationship_no', Integer, primary_key = True)
    parent_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    child_id = Column('related_ref_no', Integer, ForeignKey('bud.reference.reference_no'))
    description = Column('description', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
class Litguide(Base):
    __tablename__ = 'lit_guide'
    
    id = Column('lit_guide_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey(Reference.id))
    topic = Column('literature_topic', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    reference = relationship(Reference)
    
class LitguideFeat(Base):
    __tablename__ = 'litguide_feat'
    
    id = Column('litguide_feat_no', Integer, primary_key = True)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    litguide_id = Column('lit_guide_no', Integer, ForeignKey(Litguide.id))
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    litguide = relationship(Litguide)
    feature = relationship(Feature)
    topic = association_proxy('litguide', 'topic')
