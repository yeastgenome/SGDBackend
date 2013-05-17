'''
Created on Feb 27, 2013

@author: kpaskov
'''
from schema_conversion import cache, create_or_update, \
    create_or_update_and_remove
from schema_conversion.output_manager import OutputCreator


"""
---------------------Cache------------------------------
"""

id_to_journal = {}
id_to_book = {}
id_to_abstract = {}
id_to_author = {}
id_to_reftype = {}
tuple_to_author_ref = {}
tuple_to_reftype_ref = {}
id_to_reference = {}
id_to_bioentevidence = {}

    
"""
---------------------Create------------------------------
"""
def create_book(old_book):
    from model_new_schema.reference import Book as NewBook
    
    new_book = NewBook(old_book.title, old_book.volume_title, old_book.isbn, old_book.total_pages, old_book.publisher, old_book.publisher_location, 
                    book_id=old_book.id, date_created=old_book.date_created, created_by=old_book.created_by)
    return new_book

def create_journal(old_journal):
    from model_new_schema.reference import Journal as NewJournal
    
    new_journal = NewJournal(old_journal.abbreviation, journal_id=old_journal.id, full_name=old_journal.full_name, issn=old_journal.issn, 
                             essn=old_journal.essn, created_by=old_journal.created_by, date_created = old_journal.date_created)
    return new_journal

def create_author_reference(old_author_reference):
    from model_new_schema.reference import AuthorReference as NewAuthorReference
    
    new_author_reference = NewAuthorReference(old_author_reference.author_id, old_author_reference.reference_id, old_author_reference.order, 
                                              old_author_reference.type, author_reference_id=old_author_reference.id)
    return new_author_reference

def create_reftype_reference(old_reftype_reference):
    from model_new_schema.reference import RefReftype as NewRefReftype
    
    new_reftype_reference = NewRefReftype(ref_reftype_id=old_reftype_reference.id, reference_id=old_reftype_reference.reference_id,
                                         reftype_id=old_reftype_reference.reftype_id)
    return new_reftype_reference

def create_author(old_author):
    from model_new_schema.reference import Author as NewAuthor
    
    new_author = NewAuthor(old_author.name, author_id=old_author.id, created_by=old_author.created_by, date_created=old_author.date_created)
    return new_author

def create_abstract(old_abstract):
    from model_new_schema.reference import Abstract as NewAbstract
    
    new_abstract = NewAbstract(old_abstract.text, old_abstract.reference_id)
    return new_abstract

def create_reftype(old_reftype):
    from model_new_schema.reference import Reftype as NewReftype
    
    new_reftype = NewReftype(old_reftype.name, reftype_id=old_reftype.id, source=old_reftype.source, 
                             created_by=old_reftype.created_by, date_created=old_reftype.date_created)
    return new_reftype

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

def create_reference(old_reference):
    from model_new_schema.reference import Reference as NewReference
    
    citation = create_citation(old_reference.citation)
    name = create_name(citation)
    new_ref = NewReference(old_reference.id, old_reference.pubmed_id, old_reference.source, old_reference.status, 
                           old_reference.pdf_status, old_reference.dbxref_id, citation, old_reference.year, 
                           old_reference.date_published, old_reference.date_revised, 
                           old_reference.issue, old_reference.page, old_reference.volume, old_reference.title,
                           old_reference.journal_id, old_reference.book_id, old_reference.doi, name, 
                           old_reference.date_created, old_reference.created_by)
    return new_ref

     
"""
---------------------Convert------------------------------
"""   

def convert_reference(old_session, new_session):
    from model_new_schema.reference import Journal as NewJournal, Book as NewBook, Abstract as NewAbstract, Author as NewAuthor, \
        Reftype as NewReftype, AuthorReference as NewAuthorReference, RefReftype as NewRefReftype, Reference as NewReference

    from model_new_schema.bioentity import Bioentity as NewBioentity
        
    from model_old_schema.reference import Journal as OldJournal, Book as OldBook, Abstract as OldAbstract, Author as OldAuthor, \
        RefType as OldReftype, AuthorReference as OldAuthorReference, RefReftype as OldRefReftype, Reference as OldReference
    from model_old_schema.general import DbxrefRef as OldDbxrefRef

    #Cache journals
    key_maker = lambda x: x.id
    journal_oc = OutputCreator('journal')
    cache(NewJournal, id_to_journal, key_maker, new_session, journal_oc)
    
    #Create new journals if they don't exist, or update the database if they do.
    old_objs = old_session.query(OldJournal).all()
    values_to_check = ['full_name', 'abbreviation', 'issn', 'essn', 'publisher', 'created_by', 'date_created']
    create_or_update_and_remove(old_objs, id_to_journal, create_journal, key_maker, values_to_check, 
                     new_session, journal_oc)
    new_session.commit()
    #Cache books
    key_maker = lambda x: x.id
    book_oc = OutputCreator('book')
    cache(NewBook, id_to_book, key_maker, new_session, book_oc)
    
    #Create new books if they don't exist, or update the database if they do.
    old_objs = old_session.query(OldBook).all()
    values_to_check = ['title', 'volume_title', 'isbn', 'total_pages', 'publisher', 'publisher_location', 'created_by', 'date_created']
    create_or_update_and_remove(old_objs, id_to_book, create_book, key_maker, values_to_check, 
                     new_session, book_oc)
    new_session.commit()

    #Cache references
    key_maker = lambda x: x.id
    reference_oc = OutputCreator('reference')
    cache(NewReference, id_to_reference, key_maker, new_session, reference_oc)
    
    #Create new references if they don't exist, or update the database if they do.
    old_objs = old_session.query(OldReference).all()
    values_to_check = ['source', 'status', 'pdf_status', 'dbxref_id', 'citation_db', 'year', 'pubmed_id', 'date_published', 'date_revised',
                       'issue', 'page', 'volume', 'title', 'journal_id', 'book_id', 'doi', 'created_by', 'date_created']
    create_or_update_and_remove(old_objs, id_to_reference, create_reference, key_maker, values_to_check, 
                     new_session, reference_oc)
    
#    #Cache abstracts
#    key_maker = lambda x: x.reference_id
#    output_message = 'abstract'
#    cache(NewAbstract, id_to_abstract, key_maker, session, output_creator, output_message)
#    
#    #Create new abstracts if they don't exist, or update the database if they do.
#    old_objs = old_model.execute(model_old_schema.model.get(OldAbstract), OLD_DBUSER)
#    values_to_check = ['text']
#    create_or_update(old_objs, id_to_abstract, create_abstract, key_maker, values_to_check, 
#                     old_model, session, output_creator, output_message)
#    
#    #Cache authors
#    key_maker = lambda x: x.id
#    output_message = 'author'
#    cache(NewAuthor, id_to_author, key_maker, session, output_creator, output_message)
#    
#    #Create new authors if they don't exist, or update the database if they do.
#    old_objs = old_model.execute(model_old_schema.model.get(OldAuthor), OLD_DBUSER)
#    values_to_check = ['name', 'created_by', 'date_created']
#    create_or_update(old_objs, id_to_author, create_author, key_maker, values_to_check, 
#                     old_model, session, output_creator, output_message)
#    
#    #Cache reftypes
#    key_maker = lambda x: x.id
#    output_message = 'reftype'
#    cache(NewReftype, id_to_reftype, key_maker, session, output_creator, output_message)
#    
#    #Create new reftypes if they don't exist, or update the database if they do.
#    old_objs = old_model.execute(model_old_schema.model.get(OldReftype), OLD_DBUSER)
#    values_to_check = ['source', 'name', 'created_by', 'date_created']
#    create_or_update(old_objs, id_to_reftype, create_reftype, key_maker, values_to_check, 
#                     old_model, session, output_creator, output_message)
#    
#    #Cache reftype_refs
#    key_maker = lambda x: (x.reftype_id, x.reference_id)
#    output_message = 'reftype_ref'
#    cache(NewRefReftype, tuple_to_reftype_ref, key_maker, session, output_creator, output_message)
#    
#    #Create new reftype_refs if they don't exist, or update the database if they do.
#    old_objs = old_model.execute(model_old_schema.model.get(OldRefReftype), OLD_DBUSER)
#    values_to_check = ['reference_id', 'reftype_id']
#    create_or_update(old_objs, tuple_to_reftype_ref, create_reftype_reference, key_maker, values_to_check, 
#                     old_model, session, output_creator, output_message)
        
#    #Cache bioents with dbxref_id
#    key_maker = lambda x: x.dbxref_id
#    output_message = 'bioent with dbxref_id'
#    cache(NewBioentity, dbxref_id_to_bioent, key_maker, session, output_creator, output_message)
#    
#    #Cache bioentevidences
#    key_maker = lambda x: x.id
#    output_message = 'bioentevidences'
#    cache(NewBioentevidence, id_to_bioentevidence, key_maker, session, output_creator, output_message)
#    
#    #Create new bioentevidences if they don't exist, or update the database if they do.
#    old_objs = old_model.user_to_sessionmaker[OLD_DBUSER]().query(OldDbxrefRef).options(joinedload('dbxref')).all()
#    values_to_check = ['bioent_id']
#    create_or_update(old_objs, id_to_bioentevidence, create_bioentevidence, key_maker, values_to_check, 
#                     old_model, session, output_creator, output_message, [check_evidence])
##    
#    #Cache author_refs
#    key_maker = lambda x: (x.author_id, x.reference_id)
#    output_message = 'author_ref'
#    cache(NewAuthorReference, tuple_to_author_ref, key_maker, session, output_creator, output_message)
#    
#    #Create new author_refs if they don't exist, or update the database if they do.
#    old_objs = old_model.execute(model_old_schema.model.get(OldAuthorReference), OLD_DBUSER)
#    values_to_check = ['author_id', 'reference_id', 'order', 'type']
#    create_or_update(old_objs, tuple_to_author_ref, create_author_reference, key_maker, values_to_check, 
#                     old_model, session, output_creator, output_message)
    

    
   

