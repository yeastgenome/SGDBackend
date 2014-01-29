'''
Created on Feb 27, 2013

@author: kpaskov
'''
from convert_other.convert_auxiliary import convert_disambigs
from convert_utils import create_or_update, create_format_name
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
import logging
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
            return [NewAbstract(old_reference.id, old_reference.abstract)]
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

def create_bibentry(reference, id_to_journal, id_to_book, id_to_abstract, id_to_reftypes, id_to_authors, id_to_source):
    from model_new_schema.reference import Bibentry
    entries = []
    try:
        entries.append('PMID- ' + str(reference.pubmed_id))
    except:
        pass
    try:
        entries.append('STAT- ' + str(reference.ref_status))
    except:
        pass
    try:
        entries.append('DP  - ' + str(reference.date_published)) 
    except:
        pass
    if reference.title is not None:
        try:
            entries.append('TI  - ' + reference.title.encode('ascii', 'ignore'))
        except:
            pass
    try:
        entries.append('SO  - ' + str(id_to_source[reference.source_id]))
    except:
        pass
    try:
        entries.append('LR  - ' + str(reference.date_revised))
    except:
        pass
    try:
        entries.append('IP  - ' + str(reference.issue))
    except:
        pass
    try:
        entries.append('PG  - ' + str(reference.page))
    except:
        pass
    try:
        entries.append('VI  - ' + str(reference.volume))
    except:
        pass
        
    if reference.id in id_to_authors:
        for author in id_to_authors[reference.id]:
            try:
                entries.append('AU  - ' + str(author))
            except:
                pass
       
    if reference.id in id_to_reftypes:     
        for reftype in id_to_reftypes[reference.id]:
            try:
                entries.append('PT  - ' + str(reftype))
            except:
                pass
        
    if reference.id in id_to_abstract:
        try:
            entries.append('AB  - ' + str(id_to_abstract[reference.id]))
        except:
            pass
        
    if reference.journal_id is not None:
        journal = id_to_journal[reference.journal_id]
        try:
            entries.append('TA  - ' + str(journal.med_abbr))
        except:
            pass
        try:
            entries.append('JT  - ' + str(journal.title))
        except:
            pass
        try:
            entries.append('IS  - ' + str(journal.issn_print))
        except:
            pass

        
    if reference.book_id is not None:
        book = id_to_book[reference.book_id]
        try:
            entries.append('PL  - ' + str(book.publisher_location))
        except:
            pass
        try:
            entries.append('BTI - ' + str(book.title))
        except:
            pass
        try:
            entries.append('VTI - ' + str(book.volume_title))
        except:
            pass
        try:
            entries.append('ISBN- ' + str(book.isbn))
        except:
            pass
    ref_bib = Bibentry(reference.id, '\n'.join([str(x) for x in entries]))
    return [ref_bib]

def convert_bibentry(new_session_maker, chunk_size):
    from model_new_schema.reference import Reference as NewReference, Bibentry as NewBibentry, \
    Journal as NewJournal, Book as NewBook, Abstract as NewAbstract, \
    Reftype as NewReftype, Author as NewAuthor, AuthorReference as NewAuthorReference, \
    ReferenceReftype as NewReferenceReftype
    from model_new_schema.evelements import Source as NewSource
    
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
        id_to_source = dict([(x.id, x.display_name) for x in new_session.query(NewSource).all()])
        
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
        id_to_reftype = dict([(x.id, x) for x in new_session.query(NewReftype).all()])
        for refreftype in new_session.query(NewReferenceReftype).all():
            reference_id = refreftype.reference_id
            reftype_name = id_to_reftype[refreftype.reftype_id].display_name
            
            if reference_id in id_to_reftypes:
                id_to_reftypes[reference_id].add(reftype_name)
            else:
                id_to_reftypes[reference_id] = set([reftype_name])
        
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
                                            NewReference.id <=  min_id+chunk_size).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_bibentry(old_obj, id_to_journal, id_to_book, id_to_abstract, id_to_reftypes, id_to_authors, id_to_source)
                
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

def create_author(old_author, key_to_source):
    from model_new_schema.reference import Author as NewAuthor
    
    display_name = old_author.name
    source = key_to_source['PubMed']
    new_author = NewAuthor(old_author.id, display_name, source, old_author.date_created, old_author.created_by)
    return [new_author]

def convert_author(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.reference import Author as NewAuthor
    from model_new_schema.evelements import Source as NewSource
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
        
        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource)])
        
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
                newly_created_objs = create_author(old_obj, key_to_source)
                    
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

def create_author_reference(old_author_reference, old_id_to_author, id_to_reference, key_to_source):
    from model_new_schema.reference import AuthorReference as NewAuthorReference
    author_id = old_author_reference.author_id
    author = None if author_id not in old_id_to_author else old_id_to_author[author_id]
    reference_id = old_author_reference.reference_id
    reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
    if reference is not None:
        source = key_to_source['PubMed']
        new_author_reference = NewAuthorReference(old_author_reference.id, source, author, reference, 
                                              old_author_reference.order, old_author_reference.type, reference.date_created, reference.created_by)
        return [new_author_reference]
    else:
        return []

def convert_author_reference(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.reference import Author as NewAuthor, Reference as NewReference, AuthorReference as NewAuthorReference
    from model_new_schema.evelements import Source as NewSource
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
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource)])
        
        #Simplify author conversion
        old_id_to_key = dict([(x.id, create_format_name(x.name)) for x in old_session.query(OldAuthor).all()])
        new_key_to_author = dict([(x.unique_key(), x) for x in new_session.query(NewAuthor).all()])
        old_id_to_author = dict([(x, new_key_to_author[y]) for x, y in old_id_to_key.iteritems()])
        
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
                newly_created_objs = create_author_reference(old_obj, old_id_to_author, id_to_reference, key_to_source)
                
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
                    else:
                        print unique_key
                                
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

def create_reftype(old_reftype, key_to_source):
    from model_new_schema.reference import Reftype as NewReftype
    
    source_key = create_format_name(old_reftype.source)
    source = None if source_key not in key_to_source else key_to_source[source_key]
    
    new_reftype = NewReftype(old_reftype.id, old_reftype.name, 
                             source, old_reftype.date_created, old_reftype.created_by)
    return [new_reftype]

def convert_reftype(old_session_maker, new_session_maker):
    from model_new_schema.reference import Reftype as NewReftype
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.reference import RefType as OldReftype
    
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
        old_objs = old_session.query(OldReftype).all()

        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        #Values to check
        values_to_check =  ['source_id', 'display_name', 'link']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
            
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_reftype(old_obj, key_to_source)
            
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
--------------------- Convert ReferenceReftype ---------------------
"""

def create_reference_reftype(old_refreftype, id_to_source, id_to_reference, id_to_reftype):
    from model_new_schema.reference import ReferenceReftype as NewReferenceReftype
    
    reftype = None if old_refreftype.reftype_id not in id_to_reftype else id_to_reftype[old_refreftype.reftype_id]
    reference = None if old_refreftype.reference_id not in id_to_reference else id_to_reference[old_refreftype.reference_id]
    source = None if reftype.source_id not in id_to_source else id_to_source[reftype.source_id]
    
    if reference is not None:
        new_refreftype = NewReferenceReftype(old_refreftype.id, source, reference, reftype,
                             reftype.date_created, reftype.created_by)
        return [new_refreftype]
    else:
        return []

def convert_reference_reftype(old_session_maker, new_session_maker):
    from model_new_schema.reference import ReferenceReftype as NewReferenceReftype, Reference as NewReference, Reftype as NewReftype
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.reference import RefReftype as OldRefReftype
    
    log = logging.getLogger('convert.reference_in_depth.reference_reftype')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewReferenceReftype).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldRefReftype).all()

        #Cache
        id_to_source = dict([(x.id, x) for x in new_session.query(NewSource).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        id_to_reftype = dict([(x.id, x) for x in new_session.query(NewReftype).all()])
        
        #Values to check
        values_to_check =  ['source_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
            
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_reference_reftype(old_obj, id_to_source, id_to_reference, id_to_reftype)
            
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

def create_reference_relation(old_ref_relation, id_to_reference, key_to_source):
    from model_new_schema.reference import Referencerelation as NewReferencerelation
    
    parent_id = old_ref_relation.parent_id
    parent = None if parent_id not in id_to_reference else id_to_reference[parent_id]
    child_id = old_ref_relation.child_id
    child = None if child_id not in id_to_reference else id_to_reference[child_id]
    
    source = key_to_source['SGD']
    if parent is not None and child is not None:
        new_ref_relation = NewReferencerelation(source, None, parent, child, 
                             old_ref_relation.date_created, old_ref_relation.created_by)
        return [new_ref_relation]
    else:
        return []

def convert_reference_relation(old_session_maker, new_session_maker):
    from model_new_schema.reference import Referencerelation as NewReferencerelation, Reference as NewReference
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.reference import RefRelation as OldRefRelation
    
    log = logging.getLogger('convert.reference_in_depth.reference_relation')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewReferencerelation).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = []
        
        #Grab cached dictionaries
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldRefRelation).all()
                
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_reference_relation(old_obj, id_to_reference, key_to_source)
                
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

def create_alias(old_reference, id_to_reference, key_to_source):
    from model_new_schema.reference import Referencealias as NewReferencealias
    
    reference_id = old_reference.id
    reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
    source = key_to_source['SGD']
    new_aliases = []
    
    for dbxref in old_reference.dbxrefs:
        altid_name = dbxref.dbxref_type
        if altid_name == 'DBID Secondary':
            identifier = dbxref.dbxref_id
            new_aliases.append(NewReferencealias(identifier, source, altid_name, reference,
                                            old_reference.date_created, old_reference.created_by))
    return new_aliases

def convert_alias(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.reference import Reference as NewReference, Referencealias as NewReferencealias
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.reference import Reference as OldReference
    
    log = logging.getLogger('convert.reference_in_depth.reference_alias')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
                
        #Values to check
        values_to_check = ['source_id', 'category', 'display_name']
                
        #Grab cached dictionaries
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        
        ref_min_id = 0      
        count = 100000
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            min_id = ref_min_id + i*chunk_size
            max_id = ref_min_id + (i+1)*chunk_size
            
            #Grab all current objects
            current_objs = new_session.query(NewReferencealias).filter(NewReferencealias.reference_id >= min_id).filter(NewReferencealias.reference_id <  max_id).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = old_session.query(OldReference).filter(
                                            OldReference.id >= min_id).filter(
                                            OldReference.id <  max_id).options(
                                            joinedload('dbxrefrefs')).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_alias(old_obj, id_to_reference, key_to_source)
                
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
                
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
                                
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

def create_url(reference, key_to_source):
    from model_new_schema.reference import Referenceurl as NewReferenceurl
    
    new_urls = []
    new_urls.append(NewReferenceurl('PubMed', 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(reference.pubmed_id), key_to_source['PubMed'], 'PUBMED', reference, 
                                  None, None))
    if reference.doi is not None:
        new_urls.append(NewReferenceurl('Full-Text', 'http://dx.doi.org/' + reference.doi, key_to_source['DOI'], 'FULLTEXT', reference,
                                  None, None))
    if reference.pubmed_central_id is not None:
        new_urls.append(NewReferenceurl('PMC', 'http://www.ncbi.nlm.nih.gov/pmc/articles/' + str(reference.pubmed_central_id), key_to_source['PubMedCentral'], 'PUBMEDCENTRAL', reference, 
                                  None, None))
    return new_urls

def convert_url(new_session_maker, chunk_size):
    from model_new_schema.reference import Reference, Referenceurl as NewReferenceurl
    from model_new_schema.evelements import Source as NewSource
    
    log = logging.getLogger('convert.reference_in_depth.reference_url')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
                
        #Values to check
        values_to_check = ['display_name', 'category', 'source_id', 'reference_id']
        
        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        ref_min_id = 0      
        count = 100000
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            min_id = ref_min_id + i*chunk_size
            max_id = ref_min_id + (i+1)*chunk_size
            
            #Grab all current objects
            current_objs = new_session.query(NewReferenceurl).filter(NewReferenceurl.reference_id >= min_id).filter(NewReferenceurl.reference_id <  max_id).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
        
            #Grab old objects
            old_objs = new_session.query(Reference).filter(
                                            Reference.id >= min_id).filter(
                                            Reference.id < max_id).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_url(old_obj, key_to_source)
                
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
    #convert_abstract(old_session_maker, new_session_maker, 3000)
    
    #convert_author(old_session_maker, new_session_maker, 10000)

    #convert_author_reference(old_session_maker, new_session_maker, 10000)
    
    #convert_reftype(old_session_maker, new_session_maker)
    
    #convert_reference_reftype(old_session_maker, new_session_maker)
    
    #convert_reference_relation(old_session_maker, new_session_maker)
    
    #convert_alias(old_session_maker, new_session_maker, 3000)
    
    #convert_url(new_session_maker, 3000)
        
    #convert_bibentry(new_session_maker, 3000)
    
    from model_new_schema.reference import Reference, Author
    #convert_disambigs(new_session_maker, Reference, ['id', 'sgdid'], 'REFERENCE', None, 'convert.reference.disambigs', 3000)
    convert_disambigs(new_session_maker, Author, ['format_name', 'id'], 'AUTHOR', None, 'convert.reference.author_disambigs', 3000)
   

   

