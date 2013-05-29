'''
Created on Feb 27, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import cache, create_or_update_and_remove, ask_to_commit, \
    prepare_schema_connection
from sqlalchemy.orm import joinedload
import datetime
import model_new_schema
import model_old_schema

    


"""
---------------------Create------------------------------
"""

def create_citation(citation):
    end_of_name = citation.find(")")+1
    name = citation[:end_of_name]
    words_in_name = name.split()
    for i in range(0, len(words_in_name)):
        word = words_in_name[i]
        if len(word) > 3:
            words_in_name[i] = word.title()
    name = ' '.join(words_in_name)
    new_citation = name + citation[end_of_name:]
    new_citation = new_citation.replace('()', '')
    return new_citation

def create_name(citation):
    name = citation[:citation.find(")")+1]
    return name

def create_book(old_book):
    from model_new_schema.reference import Book as NewBook
    
    new_book = NewBook(old_book.id, old_book.title, old_book.volume_title, old_book.isbn, old_book.total_pages, 
                       old_book.publisher, old_book.publisher_location, 
                       old_book.date_created, old_book.created_by)
    return new_book

def create_journal(old_journal):
    from model_new_schema.reference import Journal as NewJournal
    
    new_journal = NewJournal(old_journal.id, old_journal.abbreviation, old_journal.full_name, old_journal.issn, 
                             old_journal.essn, old_journal.publisher, old_journal.date_created, old_journal.created_by)
    return new_journal

def create_author(old_author):
    from model_new_schema.reference import Author as NewAuthor
    
    new_author = NewAuthor(old_author.id, old_author.name, old_author.date_created, old_author.created_by)
    return new_author

def create_reftype(old_reftype):
    from model_new_schema.reference import Reftype as NewReftype
    
    new_reftype = NewReftype(old_reftype.id, old_reftype.name, old_reftype.source, 
                             old_reftype.date_created, old_reftype.created_by)
    return new_reftype

def create_abstract(old_abstract, key_to_reference):
    from model_new_schema.reference import Abstract as NewAbstract
    
    reference_id = key_to_reference[create_citation(old_abstract.reference.citation)].id
    new_abstract = NewAbstract(old_abstract.text, reference_id)
    return new_abstract

def create_author_reference(old_author_reference, key_to_author, key_to_reference):
    from model_new_schema.reference import AuthorReference as NewAuthorReference
    author_id = key_to_author[old_author_reference.author.name].id
    reference_id = key_to_reference[create_citation(old_author_reference.reference.citation)].id
    new_author_reference = NewAuthorReference(old_author_reference.id, author_id, reference_id, 
                                              old_author_reference.order, old_author_reference.type)
    return new_author_reference

def create_ref_reftype(old_ref_reftype, key_to_reftype, key_to_reference):
    from model_new_schema.reference import RefReftype as NewRefReftype
    reftype_id = key_to_reftype[old_ref_reftype.reftype.name].id
    reference_id = key_to_reference[create_citation(old_ref_reftype.reference.citation)].id
    new_ref_reftype = NewRefReftype(old_ref_reftype.id, reference_id, reftype_id)
    return new_ref_reftype

def create_reference(old_reference, key_to_journal, key_to_book):
    from model_new_schema.reference import Reference as NewReference
    
    citation = create_citation(old_reference.citation)
    name = create_name(citation)
    
    journal_id = None
    book_id = None
    journal = old_reference.journal
    if journal is not None:
        journal_id = key_to_journal[(journal.full_name, journal.abbreviation, journal.issn, journal.essn, journal.publisher)].id
    book = old_reference.book
    if book is not None:
        book_id = key_to_book[book.title].id
      
    secondary_dbxref_id = None  
    secondary_dbxref_ids = [dbxref.dbxref_id for dbxref in old_reference.dbxrefs if dbxref.dbxref_type == 'DBID Secondary']
    if len(secondary_dbxref_ids) > 1:
        print 'Too many secondary dbxref_ids'
    elif len(secondary_dbxref_ids) == 1:
        secondary_dbxref_id = secondary_dbxref_ids[0]
    
    new_ref = NewReference(old_reference.id, old_reference.pubmed_id, old_reference.source, old_reference.status, 
                           old_reference.pdf_status, old_reference.dbxref_id, secondary_dbxref_id,
                           citation, old_reference.year, 
                           old_reference.date_published, old_reference.date_revised, 
                           old_reference.issue, old_reference.page, old_reference.volume, old_reference.title,
                           journal_id, book_id, old_reference.doi, name, 
                           old_reference.date_created, old_reference.created_by)
    return new_ref

     
"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):
    from model_old_schema.reference import Journal as OldJournal, Book as OldBook, Abstract as OldAbstract, Author as OldAuthor, \
        RefType as OldReftype, AuthorReference as OldAuthorReference, RefReftype as OldRefReftype, Reference as OldReference
    from model_old_schema.general import DbxrefRef

#    # Convert journals
#    print 'Journals'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_journals = old_session.query(OldJournal).all()
#        
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_journals(new_session, old_journals)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#        
#    finally:
#        old_session.close()
#        new_session.close()
#        
#    # Convert books
#    print 'Books'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_books = old_session.query(OldBook).all()
#
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_books(new_session, old_books)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
#        
#    # Convert authors
#    print 'Authors'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_authors = old_session.query(OldAuthor).all()
#
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_authors(new_session, old_authors)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
#        
#    # Convert reftypes
#    print 'Reftype'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_reftypes = old_session.query(OldReftype).all()
#
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_reftypes(new_session, old_reftypes)
#            ask_to_commit(new_session, start_time)
#            new_session.close()  
#    finally:
#        old_session.close()
#        new_session.close()
        
    # Convert references
    print 'References'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        old_references = old_session.query(OldReference).options(joinedload('book'), joinedload('journal'), joinedload('dbxrefrefs')).all()

        success = False
        while not success:
            new_session = new_session_maker()
            success = convert_references(new_session, old_references)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
    # Convert abstracts
    print 'Abstracts'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        old_abstracts = old_session.query(OldAbstract).options(joinedload('reference')).all()

        success = False
        while not success:
            new_session = new_session_maker()
            success = convert_abstracts(new_session, old_abstracts)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
    # Convert author_references
    print 'AuthorReferences'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        old_author_references = old_session.query(OldAuthorReference).options(joinedload('reference'), joinedload('author')).all()

        success = False
        while not success:
            new_session = new_session_maker()
            success = convert_author_references(new_session, old_author_references)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
    # Convert ref_reftypes
    print 'RefReftypes'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        old_ref_reftypes = old_session.query(OldRefReftype).options(joinedload('reference'), joinedload('reftype')).all()

        success = False
        while not success:
            new_session = new_session_maker()
            success = convert_ref_reftypes(new_session, old_ref_reftypes)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
    
def convert_journals(new_session, old_journals):
    '''
    Convert Journals
    '''
    from model_new_schema.reference import Journal as NewJournal

    #Cache journals
    key_to_journal = cache(NewJournal, new_session)
    
    #Create new journals if they don't exist, or update the database if they do.
    new_journals = [create_journal(x) for x in old_journals]
    success = create_or_update_and_remove(new_journals, key_to_journal, [], new_session)
    return success
    
def convert_books(new_session, old_books):
    '''
    Convert Books
    '''
    from model_new_schema.reference import Book as NewBook

    #Cache books
    key_to_book = cache(NewBook, new_session)
    
    #Create new books if they don't exist, or update the database if they do.
    new_journals = [create_book(x) for x in old_books]
    values_to_check = ['volume_title', 'isbn', 'total_pages', 'publisher', 'publisher_location', 'created_by', 'date_created']
    success = create_or_update_and_remove(new_journals, key_to_book, values_to_check, new_session)
    return success
    
def convert_references(new_session, old_references):
    '''
    Convert References
    '''
    from model_new_schema.reference import Reference as NewReference, Journal as NewJournal, Book as NewBook
    #The following imports are needed in order to allow references to be deleted.
    #References have a relationship with Evidence, so when a reference is deleted, any associated evidence
    #must also be deleted to keep to foreign key constraints. In order to delete a piece of Evidence - 
    #apparently SQLAlchemy must load it. So it needs to know about the various subtypes of evidence.
    from model_new_schema.interaction import Interevidence
    from model_new_schema.go import Goevidence
    from model_new_schema.phenotype import Phenoevidence
    from model_new_schema.reference import AuthorReference, RefReftype, Abstract

    #Cache references, journals, and books
    key_to_reference = cache(NewReference, new_session)
    key_to_journal = cache(NewJournal, new_session)
    key_to_book = cache(NewBook, new_session)
    
    #Create new references if they don't exist, or update the database if they do.
    new_references = [create_reference(x, key_to_journal, key_to_book) for x in old_references]
    values_to_check = ['source', 'status', 'pdf_status', 'primary_dbxref_id', 'secondary_dxref_id',
                       'year', 'pubmed_id', 'date_published', 'date_revised',
                       'issue', 'page', 'volume', 'title', 'journal_id', 'book_id', 'doi', 'created_by', 'date_created']
    success = create_or_update_and_remove(new_references, key_to_reference, values_to_check, new_session)
    return success
    
def convert_authors(new_session, old_authors):
    '''
    Convert Authors
    '''
    from model_new_schema.reference import Author as NewAuthor

    #Cache authors
    key_to_author = cache(NewAuthor, new_session)
    
    #Create new authors if they don't exist, or update the database if they do.
    new_authors = [create_author(x) for x in old_authors]
    values_to_check = ['created_by', 'date_created']
    success = create_or_update_and_remove(new_authors, key_to_author, values_to_check, new_session)
    return success
    
def convert_reftypes(new_session, old_reftypes):
    '''
    Convert Reftypes
    '''
    from model_new_schema.reference import Reftype as NewReftype

    #Cache reftypes
    key_to_reftype = cache(NewReftype, new_session)
    
    #Create new reftypes if they don't exist, or update the database if they do.
    new_reftypes = [create_reftype(x) for x in old_reftypes]
    values_to_check = ['source', 'created_by', 'date_created']
    success = create_or_update_and_remove(new_reftypes, key_to_reftype, values_to_check, new_session)
    return success
    
def convert_abstracts(new_session, old_abstracts):
    '''
    Convert Abstracts
    '''
    from model_new_schema.reference import Abstract as NewAbstract, Reference as NewReference

    #Cache abstracts and references
    key_to_abstract = cache(NewAbstract, new_session)
    key_to_reference = cache(NewReference, new_session)
    
    #Create new abstracts if they don't exist, or update the database if they do.
    new_abstracts = [create_abstract(x, key_to_reference) for x in old_abstracts]
    values_to_check = ['text']
    success = create_or_update_and_remove(new_abstracts, key_to_abstract, values_to_check, new_session)  
    return success
    
def convert_author_references(new_session, old_author_references):
    '''
    Convert Abstracts
    '''
    from model_new_schema.reference import AuthorReference as NewAuthorReference, Author as NewAuthor, Reference as NewReference

    #Cache author_references
    key_to_author_references = cache(NewAuthorReference, new_session)
    key_to_author = cache(NewAuthor, new_session)
    key_to_reference = cache(NewReference, new_session)
    
    #Create new author_references if they don't exist, or update the database if they do.
    new_author_references = [create_author_reference(x, key_to_author, key_to_reference) for x in old_author_references]
    values_to_check = ['order', 'author_type']
    success = create_or_update_and_remove(new_author_references, key_to_author_references, values_to_check, new_session)    
    return success

def convert_ref_reftypes(new_session, old_ref_reftypes):
    '''
    Convert Abstracts
    '''
    from model_new_schema.reference import RefReftype as NewRefReftype, Reftype as NewReftype, Reference as NewReference

    #Cache ref_reftypes
    key_to_ref_reftypes = cache(NewRefReftype, new_session)
    key_to_reftype = cache(NewReftype, new_session)
    key_to_reference = cache(NewReference, new_session)
    
    #Create new ref_reftypes if they don't exist, or update the database if they do.
    new_ref_reftypes = [create_ref_reftype(x, key_to_reftype, key_to_reference) for x in old_ref_reftypes]
    success = create_or_update_and_remove(new_ref_reftypes, key_to_ref_reftypes, [], new_session)    
    return success
   
if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)   
   

