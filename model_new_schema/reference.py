'''
Created on Nov 7, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Reference module of the database schema.
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin, SCHEMA
from model_new_schema.pubmed import get_medline_data, MedlineJournal
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB
import datetime
  
class Reference(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'reference'

    id = Column('reference_id', Integer, primary_key = True)
    source = Column('source', String)
    status = Column('status', String)
    pdf_status = Column('pdf_status', String)
    dbxref_id = Column('dbxref_id', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    pubmed_id = Column('pubmed_id', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', String)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', Integer, ForeignKey('sprout.journal.journal_id'))
    book_id = Column('book_id', Integer, ForeignKey('sprout.book.book_id'))
    doi = Column('doi', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    name = Column('name', String)
    
    #Relationships
    journal = relationship('Journal', uselist=False)
    journal_abbrev = association_proxy('journal', 'abbreviation',
                                    creator=lambda x: Journal.as_unique(Session.object_session(self), abbreviation=x))
    
    book = relationship('Book', uselist=False)
    
    abst = relationship("Abstract", cascade='all,delete', uselist=False)
    abstract = association_proxy('abst', 'text')
        
    author_references = relationship('AuthorReference', cascade='all,delete', collection_class=attribute_mapped_collection('order'))
    
    authorNames = association_proxy('author_references', 'author_name')
    authors = association_proxy('author_references', 'author', 
                                creator=lambda k, v: AuthorReference(session=None, author=v, order=k, ar_type='Author'))
    
    reftype_references = relationship('RefReftype', cascade='all,delete',
                            collection_class=attribute_mapped_collection('id'))
    
    reftypeNames = association_proxy('reftype_references', 'reftype_name')
    reftypes = association_proxy('reftype_references', 'reftype', 
                                creator=lambda k, v: RefReftype(session=None, ref_reftype_id=k, reftype=v))

    
    #litGuides = relationship("LitGuide", cascade='all,delete')
    #litGuideTopics = association_proxy('litGuides', 'topic')
    
    #curations = relationship('RefCuration', cascade='all,delete')

    
    def __init__(self, pubmed_id, session=None, reference_id=None, source=None, status=None, pdf_status=None, dbxref_id=None, citation=None, 
                 year=None, date_published=None, date_revised=None, issue=None, page=None, volume=None, title=None, 
                 journal_id=None, book_id=None, date_created=None, created_by=None, doi=None, name=None):
        if session is None:
            self.id = reference_id
            self.pubmed_id = pubmed_id
            self.source=source
            self.status = status
            self.pdf_status = pdf_status
            self.dbxref_id = dbxref_id
            self.citation = citation
            self.year = year
            self.date_published = date_published
            self.date_revised = date_revised
            self.issue = issue
            self.page = page
            self.volume = volume
            self.title = title
            self.journal_id = journal_id
            self.book_id = book_id
            self.doi = doi
            self.name = name
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.pubmed_id = pubmed_id
            self.pdf_status='N'
            self.source='PubMed script'
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
        
            pubmed = get_medline_data(pubmed_id)
            
            #Set basic information for the reference.
            self.status = pubmed.publish_status
            self.citation = pubmed.citation
            self.year = pubmed.year
            self.pdf_status = pubmed.pdf_status
            self.pages = pubmed.pages
            self.volume = pubmed.volume
            self.title = pubmed.title
            self.issue = pubmed.issue
                        
            #Add the journal.
            self.journal = Journal.as_unique(session, abbreviation=pubmed.journal_abbrev)
        
            #Add the abstract.
            if pubmed.abstract_txt is not None and not pubmed.abstract_txt == "": 
                self.abst = Abstract.as_unique(session, reference_id = self.id, text = pubmed.abstract_txt)
                
            #Add the authors.
            order = 0
            for author_name in pubmed.authors:
                order += 1
                self.authors[order] = Author.as_unique(session, name=author_name)
                
            #Add the ref_type
            self.refType = Reftype.as_unique(session, name=pubmed.pub_type)
        
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

    id = Column('book_id', Integer, primary_key = True)
    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    def __init__(self, title, volume_title, isbn, total_pages, publisher, publisher_location, session=None, book_id=None, date_created=None, created_by=None):
        self.title = title
        self.volume_title = volume_title
        self.isbn = isbn
        self.total_pages = total_pages
        self.publisher = publisher
        self.publisher_location = publisher_location
        
        if session is None:
            self.id = book_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.title, self.total_pages, self.publisher
        return 'Book(title=%s, total_pages=%s, publisher=%s)' % data
    
class Journal(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'journal'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('journal_id', Integer, primary_key = True)
    full_name = Column('full_name', String)
    abbreviation = Column('abbreviation', String)
    issn = Column('issn', String)
    essn = Column('essn', String)
    publisher = Column('publisher', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __init__(self, abbreviation, session=None, journal_id=None, full_name=None, issn=None, essn=None, created_by=None, date_created=None):
        if session is None:
            self.id = journal_id
            self.abbreviation = abbreviation
            self.full_name = full_name
            self.issn =issn
            self.essn = essn
            self.created_by = created_by
            self.date_created = date_created
        else:
            medlineJournal = MedlineJournal(abbreviation)
            self.abbreviation = abbreviation
            self.full_name = medlineJournal.journal_title
            self.issn = medlineJournal.issn
            self.essn = medlineJournal.essn
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, abbreviation):
        return abbreviation

    @classmethod
    def unique_filter(cls, query, abbreviation):
        return query.filter(Journal.abbreviation == abbreviation)

    def __repr__(self):
        data = self.full_name, self.publisher
        return 'Journal(full_name=%s, publisher=%s)' % data
    
    
class Author(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'author'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('author_id', Integer, primary_key = True)
    name = Column('author_name', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __init__(self, name, session=None, author_id=None, created_by=None, date_created=None):
        self.name = name
        
        if session is None:
            self.id = author_id
            self.created_by = created_by
            self.date_created = date_created
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
        
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
    __tablename__ = 'author_reference'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('author_reference_id', Integer, primary_key = True)
    author_id = Column('author_id', Integer, ForeignKey('sprout.author.author_id'))
    reference_id = Column('reference_id', Integer, ForeignKey('sprout.reference.reference_id'))
    order = Column('author_order', Integer)
    type = Column('author_type', String)
        
    def __init__(self, author, order, ar_type, session=None, author_reference_id=None):
        self.author = author
        self.order = order
        self.type = ar_type
        
        if session is None:
            self.id = author_reference_id
        
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

    reference_id = Column('reference_id', Integer, ForeignKey('sprout.reference.reference_id'), primary_key = True)
    text = Column('abstract', CLOB)
   
    def __init__(self, text, reference_id, session=None):
        self.text = str(text)
        self.reference_id = reference_id
        
    @classmethod
    def unique_hash(cls, text, reference_id):
        return reference_id

    @classmethod
    def unique_filter(cls, query, text, reference_id):
        return query.filter(Abstract.reference_id == reference_id)

    def __repr__(self):
        data = self.text
        return 'Abstract(text=%s)' % data  
    
class Reftype(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'reftype'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('reftype_id', Integer, primary_key = True)
    source = Column('source', String)
    name = Column('reftype', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __init__(self, name, session=None, reftype_id=None, source=None, created_by=None, date_created=None):
        self.name = name;
        
        if session is None:
            self.id = reftype_id
            self.source = source
            self.created_by = created_by
            self.date_created = date_created
        else:
            self.source = 'NCBI'
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, name):
        return name

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(Reftype.name == name)

    def __repr__(self):
        data = self.name
        return 'RefType(name=%s)' % data    
    
class RefReftype(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'ref_reftype'
    
    id = Column('ref_reftype_id', Integer, primary_key = True)
    reference_id = Column('reference_id', Integer, ForeignKey('sprout.reference.reference_id'))
    reftype_id = Column('reftype_id', Integer, ForeignKey('sprout.reftype.reftype_id'))
        
    def __init__(self, session=None, ref_reftype_id=None, reftype=None):
        if session is None:
            self.id = ref_reftype_id
            self.reftype = reftype
        
    @classmethod
    def unique_hash(cls, reference_id, reftype_id):
        return '%s_%s_%s_%s' % (reference_id, reftype_id)  

    @classmethod
    def unique_filter(cls, query, reference_id, reftype_id):
        return query.filter(RefReftype.reference_id == reference_id, RefReftype.reftype_id == reftype_id)
    
    reftype = relationship('Reftype', lazy='joined') 
    reftype_name = association_proxy('reftype', 'name')

