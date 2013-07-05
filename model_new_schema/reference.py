'''
Created on Nov 7, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Reference module of the database schema.
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.link_maker import add_link, reference_link, author_link
from model_new_schema.misc import Url, Altid
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
    source = Column('source', String)
    status = Column('status', String)
    pubmed_id = Column('pubmed_id', Integer)
    pdf_status = Column('pdf_status', String)
    citation_db = Column('citation', String)
    year = Column('year', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', Integer)
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
    related_references = association_proxy('refrels', 'child_ref')
    
    def __init__(self, reference_id, display_name, format_name, source, status, pubmed_id, pdf_status, 
                 citation, year, date_published, date_revised, issue, page, volume, title, 
                 journal_id, book_id, doi, abstract, date_created, created_by):
        self.id = reference_id
        self.display_name = display_name
        self.format_name = format_name
        self.source=source
        self.status = status
        self.pdf_status = pdf_status
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
    
    @hybrid_property
    def reftype_str(self):
        return ', '.join([reftype.name for reftype in self.reftypes])
    @hybrid_property
    def author_str(self):
        return ', '.join([author.name_with_link for author in self.authors])
    @hybrid_property
    def related_ref_str(self):
        return ', '.join([ref.name_with_link for ref in self.related_references])
    @hybrid_property
    def url_str(self):
        return '<br>' + '<br>'.join([url.name_with_link for url in self.urls])
    @hybrid_property
    def pubmed_id_with_link(self):
        if self.pubmed_id is not None:
            return add_link(str(self.pubmed_id), self.pubmed_link, new_window=True)
        else:
            return ''
    
class Author(Base, EqualityByIDMixin):
    __tablename__ = 'author'

    id = Column('author_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    def __init__(self, author_id, display_name, format_name, date_created, created_by):
        self.id = author_id
        self.display_name = display_name
        self.format_name = format_name
        self.created_by = created_by
        self.date_created = date_created
        
    def unique_key(self):
        return self.format_name
    
    @hybrid_property
    def link(self):
        return author_link(self)
    
    @hybrid_property
    def references(self):
        sorted_references = sorted([author_ref.reference for author_ref in self.author_references], key=lambda x: x.date_published, reverse=True)
        return sorted_references
    
    @hybrid_property
    def name_with_link(self):
        return add_link(self.display_name, self.link) 
    
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
    
class ReferenceRelation(Base, EqualityByIDMixin):
    __tablename__ = 'referencerel'

    id = Column('refrel_id', Integer, primary_key = True)
    parent_id = Column('parent_reference_id', Integer, ForeignKey(Reference.id))
    child_id = Column('child_reference_id', Integer, ForeignKey(Reference.id))
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    parent_ref = relationship(Reference, uselist=False, backref=backref('refrels', passive_deletes=True), primaryjoin="ReferenceRelation.parent_id==Reference.id")
    child_ref = relationship(Reference, uselist=False, primaryjoin="ReferenceRelation.child_id==Reference.id")
    
    def __init__(self, refrel_id, parent_id, child_id, date_created, created_by):
        self.id = refrel_id
        self.parent_id = parent_id;
        self.child_id = child_id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.parent_id, self.child_id)
    
class ReferenceUrl(Url):
    __tablename__ = 'referenceurl'
    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    reference_id = Column('reference_id', ForeignKey(Reference.id))
    
    __mapper_args__ = {'polymorphic_identity': 'REFERENCE_URL',
                       'inherit_condition': id == Url.id}
    
    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('urls', passive_deletes=True))
    
    def __init__(self, url, display_name, source, reference_id, date_created, created_by):
        Url.__init__(self, url, display_name, 'REFERENCE_URL', source, date_created, created_by)
        self.reference_id = reference_id
        
    def unique_key(self):
        return (self.url, self.reference_id)
        
class ReferenceAltid(Altid):
    __tablename__ = 'referencealtid'
    
    id = Column('altid_id', Integer, ForeignKey(Altid.id), primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    
    __mapper_args__ = {'polymorphic_identity': 'REFERENCE_ALTID',
                       'inherit_condition': id == Altid.id}
        
    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('altids', passive_deletes=True))
        
    def __init__(self, identifier, source, altid_name, reference_id, date_created, created_by):
        Altid.__init__(self, identifier, 'REFERENCE_ALTID', source, altid_name, date_created, created_by)
        self.reference_id = reference_id

    
 


