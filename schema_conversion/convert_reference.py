'''
Created on Feb 27, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, ask_to_commit, \
    prepare_schema_connection, cache_by_key, cache_by_id
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

def create_display_name(citation):
    display_name = citation[:citation.find(")")+1]
    return display_name

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

def create_author_reference(old_author_reference, key_to_author, id_to_reference):
    from model_new_schema.reference import AuthorReference as NewAuthorReference
    author_key = old_author_reference.author.name
    if author_key not in key_to_author:
        print 'Author does not exist. ' + str(author_key)
        return None
    author_id = key_to_author[author_key].id
    
    reference_id = old_author_reference.reference_id
    if reference_id not in id_to_reference:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    new_author_reference = NewAuthorReference(old_author_reference.id, author_id, reference_id, 
                                              old_author_reference.order, old_author_reference.type)
    return new_author_reference

def create_reftype(old_ref_reftype, id_to_reference):
    from model_new_schema.reference import Reftype as NewReftype
    
    reference_id = old_ref_reftype.reference_id
    if reference_id not in id_to_reference:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    new_reftype = NewReftype(old_ref_reftype.id, old_ref_reftype.reftype_name, 
                             old_ref_reftype.reftype_source, reference_id)
    return new_reftype

def create_ref_relation(old_ref_relation, id_to_reference):
    from model_new_schema.reference import ReferenceRelation as NewReferenceRelation
    
    parent_id = old_ref_relation.parent_id
    if parent_id not in id_to_reference:
        print 'Reference does not exist. ' + str(parent_id)
        return None
    
    child_id = old_ref_relation.child_id
    if child_id not in id_to_reference:
        print 'Reference does not exist. ' + str(child_id)
        return None
    
    new_ref_relation = NewReferenceRelation(old_ref_relation.id, parent_id, child_id, 
                             old_ref_relation.date_created, old_ref_relation.created_by)
    return new_ref_relation

def create_url(old_ref_url):
    from model_new_schema.misc import Url as NewUrl
    
    url = old_ref_url.url.url
    if old_ref_url.url.substitution_value is not None:
        url = url.replace('_SUBSTITUTE_THIS_', str(old_ref_url.reference.pubmed_id))
    
    new_ref_relation = NewUrl(old_ref_url.id, url, old_ref_url.url.source, 
                              old_ref_url.url.date_created, old_ref_url.url.created_by)
    return new_ref_relation

def create_ref_url(old_ref_url, id_to_reference):
    from model_new_schema.reference import ReferenceUrl as NewReferenceUrl
    
    url = old_ref_url.url.url
    if old_ref_url.url.substitution_value is not None:
        url = url.replace('_SUBSTITUTE_THIS_', str(old_ref_url.reference.pubmed_id))
    
    reference_id = old_ref_url.reference_id
    if reference_id not in id_to_reference:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    new_ref_url = NewReferenceUrl(url, old_ref_url.url.source, reference_id, 
                                  old_ref_url.url.date_created, old_ref_url.url.created_by)
    return new_ref_url

def create_reference(old_reference, key_to_journal, key_to_book):
    from model_new_schema.reference import Reference as NewReference
    
    citation = create_citation(old_reference.citation)
    display_name = create_display_name(citation)
    format_name = old_reference.pubmed_id
    if format_name is None:
        format_name = old_reference.dbxref_id
    
    abstract = None
    if old_reference.abst is not None:
        abstract = old_reference.abstract
    
    journal_id = None
    journal = old_reference.journal
    if journal is not None:
        journal_key = (journal.full_name, journal.abbreviation, journal.issn, journal.essn, journal.publisher)
        if journal_key not in key_to_journal:
            print 'Journal does not exist. ' + str(journal_key)
            return None
        journal_id = key_to_journal[journal_key].id
        
    book_id = None
    book = old_reference.book
    if book is not None:
        book_key = book.title
        if book_key not in key_to_book:
            print 'Book does not exist. ' + str(book_key)
            return None
        book_id = key_to_book[book.title].id
    
    new_ref = NewReference(old_reference.id, display_name, format_name,
                           old_reference.source, old_reference.status, 
                           old_reference.pdf_status, citation, old_reference.year, 
                           old_reference.date_published, old_reference.date_revised, 
                           old_reference.issue, old_reference.page, old_reference.volume, old_reference.title,
                           journal_id, book_id, old_reference.doi, abstract,
                           old_reference.date_created, old_reference.created_by)
    return new_ref

def create_altids(old_reference, id_to_reference):
    from model_new_schema.reference import ReferenceAltid as NewReferenceAltid
    
    reference_id = old_reference.id
    if reference_id not in id_to_reference:
        return []
    
    new_alt_ids = []
    
    pubmed_id = old_reference.pubmed_id
    if pubmed_id is not None:
        new_alt_ids.append(NewReferenceAltid(pubmed_id, 'Pubmed', 'Pubmed_ID', reference_id, 
                                            old_reference.date_created, old_reference.created_by))
    for dbxref in old_reference.dbxrefs:
        identifier = dbxref.dbxref_id
        altid_name = dbxref.dbxref_type
        new_alt_ids.append(NewReferenceAltid(identifier, 'SGD', altid_name, reference_id, 
                                            old_reference.date_created, old_reference.created_by))
    return new_alt_ids

     
"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):
    from model_old_schema.reference import Journal as OldJournal, Book as OldBook, Author as OldAuthor, \
        AuthorReference as OldAuthorReference, RefReftype as OldRefReftype, Reference as OldReference, \
        RefRelation as OldRefRelation, Ref_URL as OldRef_URL, LitguideFeat as OldLitguideFeat
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
#    # Convert references
#    print 'References'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_references = old_session.query(OldReference).options(joinedload('book'), joinedload('journal'), joinedload('abst')).all()
#
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_references(new_session, old_references)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()

    # Convert altids
    print 'Altids'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        old_references = old_session.query(OldReference).options(joinedload('dbxrefrefs'), joinedload('dbxrefrefs.dbxref')).all()

        success = False
        while not success:
            new_session = new_session_maker()
            success = convert_altids(new_session, old_references)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
#        
#    # Convert author_references
#    print 'AuthorReferences'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_author_references = old_session.query(OldAuthorReference).options(joinedload('author')).all()
#
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_author_references(new_session, old_author_references)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
#        
#    # Convert reftypes
#    print 'Reftypes'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_ref_reftypes = old_session.query(OldRefReftype).options(joinedload('reftype')).all()
#
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_reftypes(new_session, old_ref_reftypes)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
#
#    # Convert reference_relations
#    print 'ReferenceRelations'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_ref_relations = old_session.query(OldRefRelation).all()
#
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_ref_relations(new_session, old_ref_relations)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
#
#    # Convert relevant urls
#    print 'Urls'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_ref_urls = old_session.query(OldRef_URL).options(joinedload('url'), joinedload('reference')).all()
#
#        success = False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_urls(new_session, old_ref_urls)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
    
def convert_journals(new_session, old_journals):
    '''
    Convert Journals
    '''
    from model_new_schema.reference import Journal as NewJournal

    #Cache journals
    key_to_journal = cache_by_key(NewJournal, new_session)
    
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
    key_to_book = cache_by_key(NewBook, new_session)
    
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

    #Cache references, journals, and books
    key_to_reference = cache_by_key(NewReference, new_session)
    key_to_journal = cache_by_key(NewJournal, new_session)
    key_to_book = cache_by_key(NewBook, new_session)
    
    #Create new references if they don't exist, or update the database if they do.
    new_references = [create_reference(x, key_to_journal, key_to_book) for x in old_references]
    values_to_check = ['display_name', 'format_name',
                       'source', 'status', 'pdf_status',
                       'year', 'date_published', 'date_revised',
                       'issue', 'page', 'volume', 'title', 'journal_id', 'book_id', 'doi', 'abstract',
                       'created_by', 'date_created']
    success = create_or_update_and_remove(new_references, key_to_reference, values_to_check, new_session)
    return success

def convert_altids(new_session, old_references):
    '''
    Convert Altids
    '''
    from model_new_schema.reference import ReferenceAltid as NewReferenceAltid, Reference as NewReference

    #Cache references, journals, and books
    key_to_altids = cache_by_key(NewReferenceAltid, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    
    #Create new altids if they don't exist, or update the database if they do.
    new_altids = []
    for old_reference in old_references:
        new_altids.extend(create_altids(old_reference, id_to_reference))
    values_to_check = ['reference_id', 'source', 'altid_name', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_altids, key_to_altids, values_to_check, new_session)
    return success
    
def convert_authors(new_session, old_authors):
    '''
    Convert Authors
    '''
    from model_new_schema.reference import Author as NewAuthor

    #Cache authors
    key_to_author = cache_by_key(NewAuthor, new_session)
    
    #Create new authors if they don't exist, or update the database if they do.
    new_authors = [create_author(x) for x in old_authors]
    values_to_check = ['created_by', 'date_created']
    success = create_or_update_and_remove(new_authors, key_to_author, values_to_check, new_session)
    return success
    
def convert_author_references(new_session, old_author_references):
    '''
    Convert AuthorReferences
    '''
    from model_new_schema.reference import AuthorReference as NewAuthorReference, Author as NewAuthor, Reference as NewReference

    #Cache author_references
    key_to_author_references = cache_by_key(NewAuthorReference, new_session)
    key_to_author = cache_by_key(NewAuthor, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    
    #Create new author_references if they don't exist, or update the database if they do.
    new_author_references = [create_author_reference(x, key_to_author, id_to_reference) for x in old_author_references]
    values_to_check = ['order', 'author_type']
    success = create_or_update_and_remove(new_author_references, key_to_author_references, values_to_check, new_session)    
    return success

def convert_reftypes(new_session, old_ref_reftypes):
    '''
    Convert Reftypes
    '''
    from model_new_schema.reference import Reftype as NewReftype, Reference as NewReference

    #Cache reftypes
    key_to_reftypes = cache_by_key(NewReftype, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    
    #Create new reftypes if they don't exist, or update the database if they do.
    new_reftypes = [create_reftype(x, id_to_reference) for x in old_ref_reftypes]
    success = create_or_update_and_remove(new_reftypes, key_to_reftypes, ['source'], new_session)    
    return success

def convert_ref_relations(new_session, old_ref_relations):
    '''
    Convert ReferenceRelations
    '''
    from model_new_schema.reference import ReferenceRelation as NewReferenceRelation, Reference as NewReference

    #Cache ref_relations
    key_to_ref_relations = cache_by_key(NewReferenceRelation, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    
    #Create new ref_relations if they don't exist, or update the database if they do.
    new_ref_relations = [create_ref_relation(x, id_to_reference) for x in old_ref_relations]
    success = create_or_update_and_remove(new_ref_relations, key_to_ref_relations, ['created_by', 'date_created'], new_session)    
    return success

def convert_urls(new_session, olf_ref_urls):
    '''
    Convert ReferenceRelations
    '''
    from model_new_schema.reference import ReferenceUrl as NewReferenceUrl, Reference as NewReference

    #Cache refurls
    key_to_ref_url = cache_by_key(NewReferenceUrl, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    
    #Create new refurls if they don't exist, or update the database if they do.
    new_ref_urls = [create_ref_url(x, id_to_reference) for x in olf_ref_urls]
    success = create_or_update_and_remove(new_ref_urls, key_to_ref_url, ['source', 'date_created', 'created_by', 'reference_id'], new_session)    
    return success
   
if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)   
   

