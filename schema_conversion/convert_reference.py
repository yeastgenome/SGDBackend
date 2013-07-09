'''
Created on Feb 27, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, \
    prepare_schema_connection, cache_by_key, cache_by_id, create_format_name, \
    execute_conversion, cache_by_key_in_range
from schema_conversion.output_manager import write_to_output_file
from sqlalchemy.orm import joinedload
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
    
    abbreviation = old_journal.abbreviation
    if old_journal.issn == '0948-5023':
        abbreviation = 'J Mol Model (Online)'
    
    new_journal = NewJournal(old_journal.id, abbreviation, old_journal.full_name, old_journal.issn, 
                             old_journal.essn, old_journal.publisher, old_journal.date_created, old_journal.created_by)
    return new_journal

def create_author(old_author):
    from model_new_schema.reference import Author as NewAuthor
    
    display_name = old_author.name
    format_name = create_format_name(display_name)
    new_author = NewAuthor(old_author.id, display_name, format_name, old_author.date_created, old_author.created_by)
    return new_author

def create_author_reference(old_author_reference, key_to_author, id_to_reference):
    from model_new_schema.reference import AuthorReference as NewAuthorReference
    author_key = create_format_name(old_author_reference.author.name)
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

def create_ref_url(old_ref_url, id_to_reference):
    from model_new_schema.reference import ReferenceUrl as NewReferenceUrl
    
    url = old_ref_url.url.url
    if old_ref_url.url.substitution_value is not None:
        url = url.replace('_SUBSTITUTE_THIS_', str(old_ref_url.reference.pubmed_id))
        
    display_name = None
    for display in old_ref_url.url.displays:
        potential_name = display.label_name
        if potential_name != 'default' and (display_name is None or len(potential_name) > len(display_name)):
            display_name = potential_name
    
    reference_id = old_ref_url.reference_id
    if reference_id not in id_to_reference:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    new_ref_url = NewReferenceUrl(url, display_name, old_ref_url.url.source, reference_id, 
                                  old_ref_url.url.date_created, old_ref_url.url.created_by)
    return new_ref_url

def create_reference(old_reference, key_to_journal, key_to_book):
    from model_new_schema.reference import Reference as NewReference
    
    citation = create_citation(old_reference.citation)
    display_name = create_display_name(citation)
    format_name = str(old_reference.pubmed_id)
    if format_name is None:
        format_name = old_reference.dbxref_id
    
    abstract = None
    if old_reference.abst is not None:
        abstract = old_reference.abstract
    
    journal_id = None
    journal = old_reference.journal
    if journal is not None:
        abbreviation = journal.abbreviation
        if journal.issn == '0948-5023':
            abbreviation = 'J Mol Model (Online)'
        journal_key = (journal.full_name, abbreviation)
        if journal_key not in key_to_journal:
            print 'Journal does not exist. ' + str(journal_key)
            return None
        journal_id = key_to_journal[journal_key].id
        
    book_id = None
    book = old_reference.book
    if book is not None:
        book_key = (book.title, book.volume_title)
        if book_key not in key_to_book:
            print 'Book does not exist. ' + str(book_key)
            return None
        book_id = key_to_book[book_key].id
        
    pubmed_id = None
    if old_reference.pubmed_id is not None:
        pubmed_id = int(old_reference.pubmed_id)
        
    year = None
    if old_reference.year is not None:
        year = int(old_reference.year)
        
    date_revised = None
    if old_reference.date_revised is not None:
        date_revised = int(old_reference.date_revised)
    
    new_ref = NewReference(old_reference.id, display_name, format_name,
                           old_reference.source, old_reference.status, pubmed_id,
                           old_reference.pdf_status, citation, year, 
                           old_reference.date_published, date_revised, 
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
        new_alt_ids.append(NewReferenceAltid(str(pubmed_id), 'Pubmed', 'Pubmed_ID', reference_id, 
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

def convert(old_session_maker, new_session_maker, ask=True):
    from model_old_schema.reference import Journal as OldJournal, Book as OldBook, Author as OldAuthor, \
        AuthorReference as OldAuthorReference, RefReftype as OldRefReftype, Reference as OldReference, \
        RefRelation as OldRefRelation
    from model_old_schema.general import Ref_URL as OldRef_URL

    # Convert journals
    write_to_output_file('Journals')
    execute_conversion(convert_journals, old_session_maker, new_session_maker, ask, 
                       old_journals=lambda old_session: old_session.query(OldJournal).all())
        
    # Convert books
    write_to_output_file('Books')
    execute_conversion(convert_books, old_session_maker, new_session_maker, ask,
                       old_books=lambda old_session: old_session.query(OldBook).all())
        
    # Convert authors
    write_to_output_file('Authors')
    execute_conversion(convert_authors, old_session_maker, new_session_maker, ask,
                       old_authors=lambda old_session: old_session.query(OldAuthor).all())
        
    # Convert references
    write_to_output_file('References')
    execute_conversion(convert_references, old_session_maker, new_session_maker, ask,
                       old_references=lambda old_session: old_session.query(OldReference).options(
                                            joinedload('book'), 
                                            joinedload('journal'), 
                                            joinedload('abst')).all())

    # Convert altids
    write_to_output_file('Altids')
    execute_conversion(convert_altids, old_session_maker, new_session_maker, ask,
                       old_references=lambda old_session: old_session.query(OldReference).options(
                                            joinedload('dbxrefrefs')).all())
    
    intervals = [0, 10000, 20000, 35000, 50000, 60000, 70000, 80000, 100000]
        
    # Convert author_references
    write_to_output_file('AuthorReferences')
    for i in range(0, len(intervals)-1):
        min_id = intervals[i]
        max_id = intervals[i+1]
        write_to_output_file('Reference ids between ' + str(min_id) + ' and ' + str(max_id))
        execute_conversion(convert_author_references, old_session_maker, new_session_maker, ask,
                       min_id=lambda old_session: min_id,
                       max_id=lambda old_session: max_id,
                       old_author_references=lambda old_session: old_session.query(OldAuthorReference).filter(
                                            OldAuthorReference.reference_id >= min_id).filter(
                                            OldAuthorReference.reference_id < max_id).options(
                                            joinedload('author')).all())
        
    # Convert reftypes
    write_to_output_file('Reftypes')
    execute_conversion(convert_reftypes, old_session_maker, new_session_maker, ask,
                       old_ref_reftypes=lambda old_session: old_session.query(OldRefReftype).options(
                                            joinedload('reftype')).all())

    # Convert reference_relations
    write_to_output_file('ReferenceRelations')
    execute_conversion(convert_ref_relations, old_session_maker, new_session_maker, ask,
                       old_ref_relations=lambda old_session: old_session.query(OldRefRelation).all())

    # Convert relevant urls
    write_to_output_file('Urls')
    for i in range(0, len(intervals)-1):
        min_id = intervals[i]
        max_id = intervals[i+1]
        write_to_output_file('Reference ids between ' + str(min_id) + ' and ' + str(max_id))
        execute_conversion(convert_urls, old_session_maker, new_session_maker, ask,
                       min_id=lambda old_session: min_id,
                       max_id=lambda old_session: max_id,
                       olf_ref_urls=lambda old_session: old_session.query(OldRef_URL).filter(
                                            OldRef_URL.reference_id >= min_id).filter(
                                            OldRef_URL.reference_id < max_id).options(
                                            joinedload('url'), 
                                            joinedload('reference')).all())

    
def convert_journals(new_session, old_journals=None):
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
    
def convert_books(new_session, old_books=None):
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
    
def convert_references(new_session, old_references=None):
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
                       'year', 
                       'date_published', 
                       'date_revised', 'name_with_link', 'citation', 'pubmed_id',
                       'issue', 'page', 'volume', 'title', 'journal_id', 'book_id', 'doi', 'abstract',
                       'created_by', 'date_created']
    success = create_or_update_and_remove(new_references, key_to_reference, values_to_check, new_session)
    return success

def convert_altids(new_session, old_references=None):
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
    
def convert_authors(new_session, old_authors=None):
    '''
    Convert Authors
    '''
    from model_new_schema.reference import Author as NewAuthor

    #Cache authors
    key_to_author = cache_by_key(NewAuthor, new_session)
    
    #Create new authors if they don't exist, or update the database if they do.
    new_authors = [create_author(x) for x in old_authors]
    values_to_check = ['created_by', 'date_created', 'display_name', 'format_name']
    success = create_or_update_and_remove(new_authors, key_to_author, values_to_check, new_session)
    return success
    
def convert_author_references(new_session, old_author_references=None, min_id=None, max_id=None):
    '''
    Convert AuthorReferences
    '''
    from model_new_schema.reference import AuthorReference as NewAuthorReference, Author as NewAuthor, Reference as NewReference

    #Cache author_references
    key_to_author_references = cache_by_key_in_range(NewAuthorReference, NewAuthorReference.reference_id, new_session, min_id, max_id)
    key_to_author = cache_by_key(NewAuthor, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    
    #Create new author_references if they don't exist, or update the database if they do.
    new_author_references = [create_author_reference(x, key_to_author, id_to_reference) for x in old_author_references]
    values_to_check = ['author_type']
    success = create_or_update_and_remove(new_author_references, key_to_author_references, values_to_check, new_session)    
    return success

def convert_reftypes(new_session, old_ref_reftypes=None):
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

def convert_ref_relations(new_session, old_ref_relations=None):
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

def convert_urls(new_session, olf_ref_urls=None, min_id=None, max_id=None):
    '''
    Convert ReferenceRelations
    '''
    from model_new_schema.reference import ReferenceUrl as NewReferenceUrl, Reference as NewReference

    #Cache refurls
    key_to_ref_url = cache_by_key_in_range(NewReferenceUrl, NewReferenceUrl.reference_id, new_session, min_id, max_id)
    id_to_reference = cache_by_id(NewReference, new_session)
    
    #Create new refurls if they don't exist, or update the database if they do.
    new_ref_urls = [create_ref_url(x, id_to_reference) for x in olf_ref_urls]
    success = create_or_update_and_remove(new_ref_urls, key_to_ref_url, ['source', 'date_created', 'created_by', 'reference_id'], new_session)    
    return success
   
if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker, False)   
   

