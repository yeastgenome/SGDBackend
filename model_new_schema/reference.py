'''
Created on Nov 7, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Reference module of the database schema.
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.misc import Url, Alias
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB

class Book(Base, EqualityByIDMixin):
    __tablename__ = 'book'

    id = Column('book_id', Integer, primary_key = True)
    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
                
    def __init__(self, book_id, title, volume_title, isbn, total_pages, publisher, publisher_location, date_created, created_by):
        self.id = book_id
        self.title = title
        self.volume_title = volume_title
        self.isbn = isbn
        self.total_pages = total_pages
        self.publisher = publisher
        self.publisher_location = publisher_location
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.title, self.volume_title)
    
class Journal(Base, EqualityByIDMixin):
    __tablename__ = 'journal'

    id = Column('journal_id', Integer, primary_key = True)
    full_name = Column('full_name', String)
    abbreviation = Column('abbreviation', String)
    issn = Column('issn', String)
    essn = Column('essn', String)
    publisher = Column('publisher', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    def __init__(self, journal_id, abbreviation, full_name, issn, essn, publisher, date_created, created_by):
        self.id = journal_id
        self.abbreviation = abbreviation
        self.full_name = full_name
        self.issn =issn
        self.essn = essn
        self.publisher = publisher
        self.created_by = created_by
        self.date_created = date_created
        
    def unique_key(self):
        return (self.full_name, self.abbreviation)

class Reference(Base, EqualityByIDMixin):
    __tablename__ = 'reference'

    id = Column('reference_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    dbxref = Column('dbxref', String)
    link = Column('obj_link', String)
    source = Column('source', String)
    
    status = Column('status', String)
    pubmed_id = Column('pubmed_id', Integer)
    pubmed_central_id = Column('pubmed_central_id', Integer)
    pdf_status = Column('pdf_status', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', Integer)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', Integer, ForeignKey(Journal.id))
    book_id = Column('book_id', Integer, ForeignKey(Book.id))
    doi = Column('doi', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships  
    book = relationship(Book, uselist=False)
    journal = relationship(Journal, uselist=False)
    abstract = association_proxy('abstract_obj', 'text')
    
    author_names = association_proxy('author_references', 'author_name')
    reftype_names = association_proxy('reftypes', 'name')
    related_references = association_proxy('refrels', 'child_ref')
    
    def __init__(self, reference_id, display_name, format_name, dbxref, link, source, 
                 status, pubmed_id, pubmed_central_id, pdf_status, citation, year, date_published, date_revised, issue, page, volume, 
                 title, journal_id, book_id, doi, date_created, created_by):
        self.id = reference_id
        self.display_name = display_name
        self.format_name = format_name
        self.dbxref = dbxref
        self.link = link
        self.source=source
        self.status = status
        self.pdf_status = pdf_status
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
        self.pubmed_id = pubmed_id
        self.pubmed_central_id = pubmed_central_id
        self.doi = doi
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.id
            
    @hybrid_property
    def authors(self):
        sorted_author_refs = sorted(list(self.author_references), key=lambda x: x.order)
        return [author_ref.author for author_ref in sorted_author_refs]   
    
    @hybrid_property
    def related_ref_str(self):
        return ', '.join([ref.name_with_link for ref in self.related_references])
    
class Bibentry(Base, EqualityByIDMixin):
    __tablename__ = 'bibentry'

    id = Column('reference_id', Integer, ForeignKey(Reference.id), primary_key = True)
    text = Column('text', CLOB)
        
    def __init__(self, reference_id, text):
        self.id = reference_id
        self.text = text
        
    def unique_key(self):
        return self.id
    
class Abstract(Base, EqualityByIDMixin):
    __tablename__ = 'abstract'

    id = Column('reference_id', Integer, ForeignKey(Reference.id), primary_key = True)
    text = Column('text', CLOB)
    
    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref("abstract_obj", uselist=False, passive_deletes=True))
        
    def __init__(self, reference_id, text):
        self.id = reference_id
        self.text = text
        
    def unique_key(self):
        return self.id
    
class Author(Base, EqualityByIDMixin):
    __tablename__ = 'author'

    id = Column('author_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_link', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    def __init__(self, author_id, display_name, format_name, link, date_created, created_by):
        self.id = author_id
        self.display_name = display_name
        self.format_name = format_name
        self.link = link
        self.created_by = created_by
        self.date_created = date_created
        
    def unique_key(self):
        return self.format_name
    
    @hybrid_property
    def references(self):
        sorted_references = sorted([author_ref.reference for author_ref in self.author_references], key=lambda x: x.date_published, reverse=True)
        return sorted_references
    
    
class AuthorReference(Base, EqualityByIDMixin):
    __tablename__ = 'author_reference'
    
    id = Column('author_reference_id', Integer, primary_key = True)
    author_id = Column('author_id', Integer, ForeignKey(Author.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    order = Column('author_order', Integer)
    author_type = Column('author_type', String)
    
    author = relationship(Author, backref=backref('author_references', passive_deletes=True), uselist=False) 
    reference = relationship(Reference, backref=backref('author_references', passive_deletes=True), uselist=False)
    author_name = association_proxy('author', 'display_name')
        
    def __init__(self, author_reference_id, author_id, reference_id, order, author_type):
        self.id = author_reference_id
        self.author_id = author_id
        self.reference_id = reference_id
        self.order = order
        self.author_type = author_type
        
    def unique_key(self):
        return (self.author_id, self.reference_id)
    
class Reftype(Base, EqualityByIDMixin):
    __tablename__ = 'reftype'

    id = Column('reftype_id', Integer, primary_key = True)
    source = Column('source', String)
    name = Column('reftype', String)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    
    #Relationships
    reference = relationship(Reference, backref=backref('reftypes', passive_deletes=True), uselist=False)
    
    def __init__(self, reftype_id, name, source, reference_id):
        self.id = reftype_id
        self.name = name;
        self.source = source
        self.reference_id = reference_id
        
    def unique_key(self):
        return (self.name, self.reference_id)
    
class ReferenceRelation(Base, EqualityByIDMixin):
    __tablename__ = 'reference_relation'

    id = Column('reference_relation_id', Integer, primary_key = True)
    parent_reference_id = Column('parent_reference_id', Integer, ForeignKey(Reference.id))
    child_reference_id = Column('child_reference_id', Integer, ForeignKey(Reference.id))
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    parent_reference = relationship(Reference, uselist=False, backref=backref('reference_relations', passive_deletes=True), primaryjoin="ReferenceRelation.parent_reference_id==Reference.id")
    child_reference = relationship(Reference, uselist=False, primaryjoin="ReferenceRelation.child_reference_id==Reference.id")
    
    def __init__(self, reference_relation_id, parent_reference_id, child_reference_id, date_created, created_by):
        self.id = reference_relation_id
        self.parent_reference_id = parent_reference_id;
        self.child_reference_id = child_reference_id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.parent_reference_id, self.child_reference_id)
    
class Referenceurl(Url):
    __tablename__ = 'referenceurl'
    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    url_type = Column('class', String)
    reference_id = Column('reference_id', ForeignKey(Reference.id))
    
    __mapper_args__ = {'polymorphic_identity': 'REFERENCE',
                       'inherit_condition': id == Url.id}
    
    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('urls', passive_deletes=True))
    
    def __init__(self, display_name, source, url, reference_id, url_type, date_created, created_by):
        Url.__init__(self, 'REFERENCE', display_name, source, url, None, date_created, created_by)
        self.reference_id = reference_id
        self.url_type = url_type
        
    def unique_key(self):
        return (self.url, self.reference_id)
    
class Referencealias(Alias):
    __tablename__ = 'referencealias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    
    __mapper_args__ = {'polymorphic_identity': 'REFERENCE',
                       'inherit_condition': id == Alias.id}
        
    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('aliases', passive_deletes=True))
        
    def __init__(self, display_name, source, category, reference_id, date_created, created_by):
        Alias.__init__(self, 'REFERENCE', display_name, source, category, date_created, created_by)
        self.reference_id = reference_id
        
    def unique_key(self):
        return (self.display_name, self.reference_id)
 


