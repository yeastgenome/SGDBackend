'''
Created on Nov 7, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Reference module of the database schema.
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.link_maker import add_link, reference_link, author_link
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
        return self.title
    
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
        return (self.full_name, self.abbreviation, self.issn, self.essn, self.publisher)

class Reference(Base, EqualityByIDMixin):
    __tablename__ = 'reference'

    id = Column('reference_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    source = Column('source', String)
    status = Column('status', String)
    pdf_status = Column('pdf_status', String)
    primary_dbxref_id = Column('primary_dbxref_id', String)
    secondary_dbxref_id = Column('secondary_dbxref_id', String)
    tertiary_dbxref_id = Column('tertiary_dbxref_id', String)
    citation_db = Column('citation', String)
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
    fulltext_link = Column('fulltext_url', String)
    abstract = Column('abstract', CLOB)
    type = "REFERENCE"
    
    #Relationships  
    book = relationship(Book, uselist=False)
    journal = relationship(Journal, uselist=False)
    
    author_names = association_proxy('author_references', 'author_name')
    reftype_names = association_proxy('reftypes', 'name')
    
    def __init__(self, reference_id, pubmed_id, display_name, format_name, source, status, pdf_status, 
                 primary_dbxref_id, secondary_dbxref_id,tertiary_dbxref_id,
                 citation, year, date_published, date_revised, issue, page, volume, title, 
                 journal_id, book_id, doi, abstract, date_created, created_by):
        self.id = reference_id
        self.pubmed_id = pubmed_id
        self.display_name = display_name
        self.format_name = format_name
        self.source=source
        self.status = status
        self.pdf_status = pdf_status
        self.primary_dbxref_id = primary_dbxref_id
        self.secondary_dbxref_id = secondary_dbxref_id
        self.tertiary_dbxref_id = tertiary_dbxref_id
        self.citation_db = citation
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
        self.abstract = abstract

        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.citation_db
        
    @hybrid_property
    def authors(self):
        sorted_author_refs = sorted(list(self.author_references), key=lambda x: x.order)
        return [author_ref.author for author_ref in sorted_author_refs]   
    @hybrid_property
    def citation(self):
        return add_link(self.display_name, self.link) + self.citation_db[self.citation_db.find(')')+1:] + self.small_pmid
    @hybrid_property
    def description(self):
        return self.title
      
    @hybrid_property
    def link(self):
        return reference_link(self)
    @hybrid_property
    def small_pmid(self):
        if self.pubmed_id is None:
            return ''
        else:
            return ' <small>PMID:' + str(self.pubmed_id) + '</small>'
    @hybrid_property
    def name_with_link(self):
        return add_link(self.display_name, self.link) + self.small_pmid
    
    @hybrid_property
    def pubmed_link(self):
        return 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(self.pubmed_id)
    
    @hybrid_property
    def search_entry_title(self):
        return self.author_year_with_link
    @hybrid_property
    def search_description(self):
        #return self.abst.text
        return self.title
    @hybrid_property
    def search_additional(self):
        if self.pubmed_id is not None:
            return 'Pubmed ID: ' + str(self.pubmed_id)
        return None
    @hybrid_property
    def search_entry_type(self):
        return 'Reference'
    
class Author(Base, EqualityByIDMixin):
    __tablename__ = 'author'

    id = Column('author_id', Integer, primary_key = True)
    name = Column('author_name', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    def __init__(self, author_id, name, date_created, created_by):
        self.id = author_id
        self.name = name
        self.created_by = created_by
        self.date_created = date_created
        
    def unique_key(self):
        return self.name
    
    @hybrid_property
    def link(self):
        return author_link(self)
    
    @hybrid_property
    def references(self):
        sorted_references = sorted([author_ref.reference for author_ref in self.author_references], key=lambda x: x.date_published, reverse=True)
        return sorted_references
    
    @hybrid_property
    def name_with_link(self):
        return add_link(self.name, self.link) 
    
class AuthorReference(Base, EqualityByIDMixin):
    __tablename__ = 'author_reference'
    
    id = Column('author_reference_id', Integer, primary_key = True)
    author_id = Column('author_id', Integer, ForeignKey('sprout.author.author_id'))
    reference_id = Column('reference_id', Integer, ForeignKey('sprout.reference.reference_id'))
    order = Column('author_order', Integer)
    author_type = Column('author_type', String)
    
    author = relationship(Author, backref=backref('author_references', passive_deletes=True), uselist=False) 
    reference = relationship(Reference, backref=backref('author_references', passive_deletes=True), uselist=False)
    author_name = association_proxy('author', 'name')
        
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

        

    
 


