'''
Created on Nov 7, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Reference module of the database schema.
'''
from model_old_schema import Base
from model_old_schema.config import SCHEMA
from model_old_schema.feature import Feature
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Integer, String
       
class Reference(Base):
    __tablename__ = 'reference'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

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
    journal_id = Column('journal_no', String, ForeignKey('bud.journal.journal_no'))
    book_id = Column('book_no', String, ForeignKey('bud.book.book_no'))
    doi = Column('doi', String)
    
    #Relationships
    journal = relationship('Journal', uselist=False)
    book = relationship('Book', uselist=False)
    
    abstract_table = Table('abstract', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True)
    abstract = column_property(
        select([abstract_table.c.abstract], abstract_table.c.reference_no==id)
    )
    
    features = relationship(Feature, secondary= Table('ref_curation', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True), backref='references')
    
    authors = relationship("Author", secondary= Table('author_editor', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    authorNames = association_proxy('authors', 'name')
    
    refTypes = relationship("RefType", secondary= Table('ref_reftype', Base.metadata, autoload=True, schema=SCHEMA, extend_existing=True))
    refTypeNames = association_proxy('refTypes', 'name')
    
    litGuides = relationship("LitGuide")
    litGuideTopics = association_proxy('litGuides', 'topic')

    def __repr__(self):
        data = self.title, self.pubmed_id
        return 'Reference(title=%s, pubmed_id=%s)' % data
    
class Book(Base):
    __tablename__ = 'book'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('book_no', Integer, primary_key = True)
    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', Integer)

    def __repr__(self):
        data = self.title, self.total_pages, self.publisher
        return 'Book(title=%s, total_pages=%s, publisher=%s)' % data
    
class Journal(Base):
    __tablename__ = 'journal'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('journal_no', Integer, primary_key = True)
    full_name = Column('full_name', String)
    abbreviation = Column('abbreviation', String)
    issn = Column('issn', String)
    essn = Column('essn', Integer)
    publisher = Column('publisher', String)

    def __repr__(self):
        data = self.full_name, self.publisher
        return 'Journal(full_name=%s, publisher=%s)' % data
    
class RefTemp(Base):
    __tablename__ = 'ref_temp'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_temp_no', Integer, primary_key = True)
    pubmed_id = Column('pubmed', Integer)
    citation = Column('citation', String)
    fulltext_url = Column('fulltext_url', String)
    abstract = Column('abstract', String)
    
    def createRefBad(self):
        return RefBad(self.pubmed_id)

    def __repr__(self):
        data = self.pubmed_id
        return 'RefTemp(pubmed_id=%s)' % data
    
class RefBad(Base):
    __tablename__ = 'ref_bad'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    pubmed_id = Column('pubmed', Integer, primary_key = True)
    dbxref_id = Column('dbxref_id', String)
    
    def __init__(self, pubmed_id, dbxref_id=None):
        self.pubmed_id = pubmed_id
        self.dbxref_id = dbxref_id

    def __repr__(self):
        data = self.pubmed_id, self.dbxref_id
        return 'RefBad(pubmed_id=%s, dbxref_id=%s)' % data    
    
class Author(Base):
    __tablename__ = 'author'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('author_no', Integer, primary_key = True)
    name = Column('author_name', String)

    def __repr__(self):
        data = self.name
        return 'Author(name=%s)' % data    
    
class RefType(Base):
    __tablename__ = 'ref_type'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_type_no', Integer, primary_key = True)
    source = Column('source', String)
    name = Column('ref_type', String)


    def __repr__(self):
        data = self.name
        return 'RefType(name=%s)' % data    
    
class LitGuide(Base):
    __tablename__ = 'lit_guide'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('lit_guide_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    topic = Column('literature_topic', String)


    def __repr__(self):
        data = self.topic, self.reference_id
        return 'LitGuide(topic=%s, reference_id=%s)' % data  

