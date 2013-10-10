'''
Created on Feb 27, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, set_up_logging, prepare_schema_connection, create_format_name
from mpmath import ceil
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
from convert_utils.link_maker import author_link
import logging
import model_new_schema
import model_old_schema
import sys

#Recorded times: 
#Maitenance (cherry-vm08): 51:17
#First Load (sgd-ng1): 35:28
#Maitenance (sgd-ng1): 26:20

"""
--------------------- Convert Abstract ---------------------
"""

def create_abstract(old_reference, reference_ids):
    from model_new_schema.reference import Abstract as NewAbstract
    if old_reference.abst is not None:
        if old_reference.id in reference_ids:
            return [NewAbstract(old_reference.id, str(old_reference.abstract))]
    return None

def convert_abstract(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.reference import Reference as NewReference, Abstract as NewAbstract
    from model_old_schema.reference import Reference as OldReference
    
    log = logging.getLogger('convert.reference_in_depth.abstract')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()
        
        #Values to check
        values_to_check = ['text']
                
        #Grab cached dictionaries
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
        
        count = old_session.query(func.max(OldReference.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewAbstract).filter(NewAbstract.id >= min_id).filter(NewAbstract.id <=  min_id+chunk_size).all()
            
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = old_session.query(OldReference).filter(
                                            OldReference.id >= min_id).filter(
                                            OldReference.id <=  min_id+chunk_size).options(
                                            joinedload('abst')).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_abstract(old_obj, reference_ids)
                
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
--------------------- Convert Bibentry ---------------------
"""

def create_bibentry(reference, id_to_journal, id_to_book, id_to_abstract, id_to_reftypes, id_to_authors):
    from model_new_schema.reference import Bibentry
    entries = []
    entries.append('PMID- ' + str(reference.pubmed_id)) 
    entries.append('STAT- ' + str(reference.status))
    entries.append('DP  - ' + str(reference.date_published)) 
    entries.append('TI  - ' + str(reference.title))
    entries.append('SO  - ' + str(reference.source)) 
    entries.append('LR  - ' + str(reference.date_revised)) 
    entries.append('IP  - ' + str(reference.issue)) 
    entries.append('PG  - ' + str(reference.page)) 
    entries.append('VI  - ' + str(reference.volume)) 
        
    if reference.id in id_to_authors:
        for author in id_to_authors[reference.id]:
            entries.append('AU  - ' + author)
            
    if reference.id in id_to_reftypes:
        for reftype in id_to_reftypes[reference.id]:
            entries.append('PT  - ' + reftype)
        
    if reference.id in id_to_abstract:
        entries.append('AB  - ' + id_to_abstract[reference.id])
        
    if reference.journal_id is not None:
        journal = id_to_journal[reference.journal_id]
        entries.append('TA  - ' + str(journal.abbreviation)) 
        entries.append('JT  - ' + str(journal.full_name)) 
        entries.append('IS  - ' + str(journal.issn)) 

        
    if reference.book_id is not None:
        book = id_to_book[reference.book_id]
        entries.append('PL  - ' + str(book.publisher_location)) 
        entries.append('BTI - ' + str(book.title))
        entries.append('VTI - ' + str(book.volume_title)) 
        entries.append('ISBN- ' + str(book.isbn))     
    ref_bib = Bibentry(reference.id, '\n'.join(entries))
    return [ref_bib]

def convert_bibentry(new_session_maker, chunk_size):
    from model_new_schema.reference import Reference as NewReference, Bibentry as NewBibentry, \
    Journal as NewJournal, Book as NewBook, Abstract as NewAbstract, \
    Reftype as NewReftype, Author as NewAuthor, AuthorReference as NewAuthorReference
    
    log = logging.getLogger('convert.reference_in_depth.bibentry')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        
        #Values to check
        values_to_check = ['text']
        
        #Grab cached dictionaries
        id_to_journal = dict([(x.id, x) for x in new_session.query(NewJournal).all()])
        id_to_book = dict([(x.id, x) for x in new_session.query(NewBook).all()])
        id_to_abstract = dict([(x.id, x.text) for x in new_session.query(NewAbstract).all()])
        
        id_to_authors = {}
        id_to_author = dict([(x.id, x) for x in new_session.query(NewAuthor).all()])
        for ar in new_session.query(NewAuthorReference).all():
            reference_id = ar.reference_id
            author_name = id_to_author[ar.author_id].display_name
            
            if reference_id in id_to_authors:
                id_to_authors[reference_id].add(author_name)
            else:
                id_to_authors[reference_id] = set([author_name])
        
        id_to_reftypes = {}
        reftypes = new_session.query(NewReftype).all()
        for reftype in reftypes:
            reference_id = reftype.reference_id
            reftype_name = reftype.name
            
            if reference_id in id_to_reftypes:
                id_to_reftypes[reference_id].add(reftype_name)
            else:
                id_to_reftypes[reference_id] = set([author_name])
        
        count = new_session.query(func.max(NewReference.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewBibentry).filter(NewBibentry.id >= min_id).filter(NewBibentry.id <=  min_id+chunk_size).all()
            
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = new_session.query(NewReference).filter(
                                            NewReference.id >= min_id).filter(
                                            NewReference.id <=  min_id+chunk_size).options(joinedload('author_references')).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_bibentry(old_obj, id_to_journal, id_to_book, id_to_abstract, id_to_reftypes, id_to_authors)
                
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
        
    log.info('complete')
       
"""
--------------------- Convert Author ---------------------
"""

def create_author_id(old_author_id):
    return old_author_id

def create_author(old_author):
    from model_new_schema.reference import Author as NewAuthor
    
    display_name = old_author.name
    format_name = create_format_name(display_name)
    link = author_link(format_name)
    new_author = NewAuthor(create_author_id(old_author.id), display_name, format_name, link, old_author.date_created, old_author.created_by)
    return [new_author]

def convert_author(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.reference import Author as NewAuthor
    from model_old_schema.reference import Author as OldAuthor
    
    log = logging.getLogger('convert.reference_in_depth.author')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewAuthor).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['display_name', 'link', 'created_by', 'date_created']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        used_unique_keys = set()
        
        old_session = old_session_maker()
        
        count = old_session.query(func.max(OldAuthor.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewAuthor).filter(NewAuthor.id >= min_id).filter(NewAuthor.id < min_id+chunk_size).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = old_session.query(OldAuthor).filter(
                                            OldAuthor.id >= min_id).filter(
                                            OldAuthor.id <  min_id+chunk_size).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_author(old_obj)
                    
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
                        
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
                        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id + chunk_size
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Author Reference ---------------------
"""

def create_author_reference_id(old_author_reference_id):
    return old_author_reference_id

def create_author_reference(old_author_reference, old_id_to_new_id_author, reference_ids):
    from model_new_schema.reference import AuthorReference as NewAuthorReference
    author_id = old_author_reference.author_id
    if author_id not in old_id_to_new_id_author:
        print 'Author does not exist. ' + str(author_id)
        return None
    author_id = old_id_to_new_id_author[author_id]
    
    reference_id = old_author_reference.reference_id
    if reference_id not in reference_ids:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    new_author_reference = NewAuthorReference(create_author_reference_id(old_author_reference.id), author_id, reference_id, 
                                              old_author_reference.order, old_author_reference.type)
    return [new_author_reference]

def convert_author_reference(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.reference import Author as NewAuthor, Reference as NewReference, AuthorReference as NewAuthorReference
    from model_old_schema.reference import AuthorReference as OldAuthorReference, Author as OldAuthor
    
    log = logging.getLogger('convert.reference_in_depth.author_reference')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()
        
        #Values to check
        values_to_check = ['author_type']
        
        #Grab cached dictionaries
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
        
        #Simplify author conversion
        old_id_to_key = dict([(x.id, create_format_name(x.name)) for x in old_session.query(OldAuthor).all()])
        new_key_to_id = dict([(x.unique_key(), x.id) for x in new_session.query(NewAuthor).all()])
        old_id_to_new_id_author = dict([(x, new_key_to_id[y]) for x, y in old_id_to_key.iteritems()])
        
        used_unique_keys = set()
        
        count = old_session.query(func.max(OldAuthorReference.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewAuthorReference).filter(NewAuthorReference.id >= min_id).filter(NewAuthorReference.id < min_id+chunk_size).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = old_session.query(OldAuthorReference).filter(
                                            OldAuthorReference.id >= min_id).filter(
                                            OldAuthorReference.id <  min_id+chunk_size).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_author_reference(old_obj, old_id_to_new_id_author, reference_ids)
                
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
                                
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
                        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id + chunk_size
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')

"""
--------------------- Convert Reftype ---------------------
"""

def create_reftype_id(old_reftype_id):
    return old_reftype_id

def create_reftype(old_ref_reftype, reference_ids):
    from model_new_schema.reference import Reftype as NewReftype
    
    reference_id = old_ref_reftype.reference_id
    if reference_id not in reference_ids:
        return None
    
    new_reftype = NewReftype(create_reftype_id(old_ref_reftype.id), old_ref_reftype.reftype_name, 
                             old_ref_reftype.reftype_source, reference_id)
    return [new_reftype]

def convert_reftype(old_session_maker, new_session_maker):
    from model_new_schema.reference import Reference as NewReference, Reftype as NewReftype
    from model_old_schema.reference import RefReftype as OldRefReftype
    
    log = logging.getLogger('convert.reference_in_depth.reftype')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewReftype).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldRefReftype).options(joinedload('reftype')).all()
        
        #Values to check
        values_to_check =  ['source']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
                
        #Grab cached dictionaries
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
            
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_reftype(old_obj, reference_ids)
            
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
--------------------- Convert Reference Relation ---------------------
"""

def create_reference_relation_id(old_reference_relation_id):
    return old_reference_relation_id

def create_reference_relation(old_ref_relation, reference_ids):
    from model_new_schema.reference import ReferenceRelation as NewReferenceRelation
    
    parent_id = old_ref_relation.parent_id
    if parent_id not in reference_ids:
        print 'Reference does not exist. ' + str(parent_id)
        return None
    
    child_id = old_ref_relation.child_id
    if child_id not in reference_ids:
        print 'Reference does not exist. ' + str(child_id)
        return None
    
    new_ref_relation = NewReferenceRelation(old_ref_relation.id, parent_id, child_id, 
                             old_ref_relation.date_created, old_ref_relation.created_by)
    return [new_ref_relation]

def convert_reference_relation(old_session_maker, new_session_maker):
    from model_new_schema.reference import ReferenceRelation as NewReferenceRelation, Reference as NewReference
    from model_old_schema.reference import RefRelation as OldRefRelation
    
    log = logging.getLogger('convert.reference_in_depth.reference_relation')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewReferenceRelation).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['created_by', 'date_created']
        
        #Grab cached dictionaries
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldRefRelation).all()
                
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_reference_relation(old_obj, reference_ids)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    
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
--------------------- Convert Reference Alias ---------------------
"""

def create_alias(old_reference, reference_ids):
    from model_new_schema.reference import Referencealias as NewReferencealias
    
    reference_id = old_reference.id
    if reference_id not in reference_ids:
        return []
    
    new_aliases = []
    
    pubmed_id = old_reference.pubmed_id
    if pubmed_id is not None:
        new_aliases.append(NewReferencealias(str(pubmed_id), 'Pubmed', 'Pubmed_ID', reference_id, 
                                            old_reference.date_created, old_reference.created_by))
    for dbxref in old_reference.dbxrefs:
        identifier = dbxref.dbxref_id
        altid_name = dbxref.dbxref_type
        new_aliases.append(NewReferencealias(identifier, 'SGD', altid_name, reference_id, 
                                            old_reference.date_created, old_reference.created_by))
    return new_aliases

def convert_alias(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.reference import Reference as NewReference, Referencealias as NewReferencealias
    from model_old_schema.reference import Reference as OldReference
    
    log = logging.getLogger('convert.reference_in_depth.reference_alias')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
                
        #Values to check
        values_to_check = ['source', 'category', 'date_created', 'created_by']
                
        #Grab cached dictionaries
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        
        count = old_session.query(func.max(OldReference.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewReferencealias).filter(NewReferencealias.reference_id >= min_id).filter(NewReferencealias.reference_id <=  min_id+chunk_size).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = old_session.query(OldReference).filter(
                                            OldReference.id >= min_id).filter(
                                            OldReference.id <=  min_id+chunk_size).options(
                                            joinedload('dbxrefrefs')).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_alias(old_obj, reference_ids)
                
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
--------------------- Convert Reference URL ---------------------
"""

def create_url(reference):
    from model_new_schema.reference import Referenceurl as NewReferenceurl
    
    new_urls = []
    new_urls.append(NewReferenceurl('PubMed', 'PubMed', 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(reference.pubmed_id), 
                                  reference.id, 'PUBMED', None, None))
    if reference.doi is not None:
        new_urls.append(NewReferenceurl('Full-Text', 'DOI', 'http://dx.doi.org/' + reference.doi, 
                                  reference.id, 'FULLTEXT', None, None))
    if reference.pubmed_central_id is not None:
        new_urls.append(NewReferenceurl('PMC', 'PubMedCentral', 'http://www.ncbi.nlm.nih.gov/pmc/articles/' + str(reference.pubmed_central_id), 
                                  reference.id, 'PUBMEDCENTRAL', None, None))
    return new_urls

def convert_url(new_session_maker, chunk_size):
    from model_new_schema.reference import Reference, Referenceurl as NewReferenceurl
    
    log = logging.getLogger('convert.reference_in_depth.reference_url')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
                
        #Values to check
        values_to_check = ['display_name', 'category', 'source', 'date_created', 'created_by', 'reference_id', 'url_type']
        
        count = new_session.query(func.max(Reference.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewReferenceurl).filter(NewReferenceurl.reference_id >= min_id).filter(NewReferenceurl.reference_id <=  min_id+chunk_size).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = new_session.query(Reference).filter(
                                            Reference.id >= min_id).filter(
                                            Reference.id <=  min_id+chunk_size).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_url(old_obj)
                
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
        
    log.info('complete')
     
"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):
    log = set_up_logging('convert.reference_in_depth')
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
            
    log.info('begin')
    
    convert_abstract(old_session_maker, new_session_maker, 3000)
    
    convert_author(old_session_maker, new_session_maker, 10000)
    
    convert_author_reference(old_session_maker, new_session_maker, 10000)
    
    convert_reftype(old_session_maker, new_session_maker)
    
    convert_reference_relation(old_session_maker, new_session_maker)
    
    convert_alias(old_session_maker, new_session_maker, 3000)
    
    convert_url(new_session_maker, 3000)
        
    convert_bibentry(new_session_maker, 3000)
    
    log.info('complete')
   
if __name__ == "__main__":
    from convert_all import new_config, old_config
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)   
   

