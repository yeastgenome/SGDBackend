'''
Created on Feb 27, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, set_up_logging, prepare_connections, \
    create_format_name
from convert_utils.link_maker import reference_link
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
import logging
import requests
import sys

#Recorded times: 
#Maitenance (cherry-vm08): 51:17
#First Load (sgd-ng1): 35:28
#Maitenance (sgd-ng1): 26:20

"""
--------------------- Convert Journal ---------------------
"""
    
def create_journal_id(old_journal_id):
    return old_journal_id

def create_journal(old_journal):
    from model_new_schema.reference import Journal as NewJournal
    
    abbreviation = old_journal.abbreviation
    if old_journal.issn == '0948-5023':
        abbreviation = 'J Mol Model (Online)'
    
    new_journal = NewJournal(create_journal_id(old_journal.id), abbreviation, old_journal.full_name, old_journal.issn, 
                             old_journal.essn, old_journal.publisher, old_journal.date_created, old_journal.created_by)
    return [new_journal]

def convert_journal(old_session_maker, new_session_maker):
    from model_new_schema.reference import Journal as NewJournal
    from model_old_schema.reference import Journal as OldJournal
    
    log = logging.getLogger('convert.reference.journal')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewJournal).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['issn', 'essn', 'publisher', 'created_by', 'date_created']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldJournal).all()
        
        used_unique_keys = set()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_journal(old_obj)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    new_id = newly_created_obj.id
                    if unique_key not in used_unique_keys:
                        current_obj_by_id = None if new_id not in id_to_current_obj else id_to_current_obj[new_id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                        used_unique_keys.add(unique_key)
                        
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                        
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()
        
        #Commit
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Book ---------------------
"""
    
def create_book_id(old_book_id):
    return old_book_id

def create_book(old_book):
    from model_new_schema.reference import Book as NewBook
    
    new_book = NewBook(create_book_id(old_book.id), old_book.title, old_book.volume_title, old_book.isbn, old_book.total_pages, 
                       old_book.publisher, old_book.publisher_location, 
                       old_book.date_created, old_book.created_by)
    return [new_book]

def convert_book(old_session_maker, new_session_maker):
    from model_new_schema.reference import Book as NewBook
    from model_old_schema.reference import Book as OldBook
    
    log = logging.getLogger('convert.reference.book')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewBook).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['isbn', 'total_pages', 'publisher', 'publisher_location', 'created_by', 'date_created']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldBook).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_book(old_obj)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                        
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()
        
        #Commit
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Reference ---------------------
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

def get_pubmed_central_ids(pubmed_ids, chunk_size=200):
    pubmed_id_to_central_id = {}
    count = len(pubmed_ids)
    num_chunks = ceil(1.0*count/chunk_size)
    min_id = 0
    for i in range(0, num_chunks):
        chunk_of_pubmed_ids = pubmed_ids[min_id:min_id+chunk_size]
        url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pmc&id='
        url = url + '&id='.join([str(x) for x in chunk_of_pubmed_ids])
        r = requests.get(url)
        xml = str(r.text)
        pieces = xml.split('<LinkSet>')
        j = 0
        for piece in pieces[1:]:
            pubmed_id = chunk_of_pubmed_ids[j]
            linksets = piece.split('<LinkSetDb>')
            pubmed_id_to_central_id[pubmed_id] = None
            for linkset in linksets[1:]:
                if '<LinkName>pubmed_pmc</LinkName>' in linkset:
                    pubmed_central_id = int(linkset[linkset.index('<Id>')+4:linkset.index('</Id>')])
                    pubmed_id_to_central_id[pubmed_id] = pubmed_central_id
            j = j+1
        min_id = min_id + chunk_size
    return pubmed_id_to_central_id

def create_reference(old_reference, key_to_journal, key_to_book, pubmed_id_to_pubmed_central_id, key_to_source):
    from model_new_schema.reference import Reference as NewReference
    
    citation = create_citation(old_reference.citation)
    display_name = create_display_name(citation)
    format_name = str(old_reference.pubmed_id)
    if format_name is None:
        format_name = old_reference.dbxref_id
        
    link = reference_link(format_name)
    
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
    pubmed_central_id = None
    if old_reference.pubmed_id is not None:
        pubmed_id = int(old_reference.pubmed_id)
        pubmed_central_id = pubmed_id_to_pubmed_central_id[pubmed_id]
        
    year = None
    if old_reference.year is not None:
        year = int(old_reference.year)
        
    date_revised = None
    if old_reference.date_revised is not None:
        date_revised = int(old_reference.date_revised)
        
    source_key = create_format_name(old_reference.source)
    if source_key in key_to_source:
        source_id = key_to_source[source_key].id
    else:
        print 'Source not found.' + source_key
        return None
    
    new_ref = NewReference(old_reference.id, display_name, format_name, old_reference.dbxref_id, link, source_id, 
                           old_reference.status, pubmed_id, pubmed_central_id,
                           old_reference.pdf_status, citation, year, 
                           old_reference.date_published, date_revised, 
                           old_reference.issue, old_reference.page, old_reference.volume, old_reference.title,
                           journal_id, book_id, old_reference.doi,
                           old_reference.date_created, old_reference.created_by)
    return [new_ref]

def convert_reference(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.reference import Reference as NewReference, Book as NewBook, Journal as NewJournal
    from model_new_schema.evelement import Source as NewSource
    from model_old_schema.reference import Reference as OldReference
    
    log = logging.getLogger('convert.reference.reference')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
                
        #Values to check
        values_to_check = ['display_name', 'format_name', 'link', 'source_id', 'dbxref',
                       'status', 'pubmed_id', 'pubmed_central_id', 'pdf_status', 'year', 'date_published', 
                       'date_revised', 'issue', 'page', 'volume', 'title',
                       'journal_id', 'book_id', 'doi',
                       'created_by', 'date_created']
                
        #Grab cached dictionaries
        key_to_journal = dict([(x.unique_key(), x) for x in new_session.query(NewJournal).all()])
        key_to_book = dict([(x.unique_key(), x) for x in new_session.query(NewBook).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        
        used_unique_keys = set()
        
        count = old_session.query(func.max(OldReference.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewReference).filter(NewReference.id >= min_id).filter(NewReference.id <=  min_id+chunk_size).all()
            
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = old_session.query(OldReference).filter(
                                            OldReference.id >= min_id).filter(
                                            OldReference.id <=  min_id+chunk_size).options(
                                            joinedload('book'), 
                                            joinedload('journal')).all()
                                            
            old_pubmed_ids = [x.pubmed_id for x in old_objs if x.pubmed_id is not None]
            pubmed_id_to_pubmed_central_id = get_pubmed_central_ids(old_pubmed_ids)
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_reference(old_obj, key_to_journal, key_to_book, pubmed_id_to_pubmed_central_id, key_to_source)
                
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        if unique_key not in used_unique_keys:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                            
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                            if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_id.id)
                            if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_key.id)
                            used_unique_keys.add(unique_key)
                            
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
                        
            min_id = min_id + chunk_size + 1
                        
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()
        
        #Commit
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')


     
"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):
    log = set_up_logging('convert.reference')
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
            
    log.info('begin')
        
    convert_journal(old_session_maker, new_session_maker)
    
    convert_book(old_session_maker, new_session_maker)
    
    convert_reference(old_session_maker, new_session_maker, 3000)
    
    log.info('complete')
   
if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)   
   

