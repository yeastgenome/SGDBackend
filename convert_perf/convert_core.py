'''
Created on Oct 29, 2013

@author: kpaskov
'''
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
import json
import logging
import sys

"""
--------------------- Convert Disambig ---------------------
"""

def create_disambig(disambig_json):
    from model_perf_schema.core import Disambig
    return Disambig(disambig_json['id'], disambig_json['disambig_key'], disambig_json['class_type'], disambig_json['subclass_type'], disambig_json['identifier'])

def update_disambig(disambig_json, disambig):
    changed = False
    if disambig.disambig_key != disambig_json['disambig_key']:
        disambig.disambig_key = disambig_json['disambig_key']
        changed = True
    if disambig.class_type != disambig_json['class_type']:
        disambig.class_type = disambig_json['class_type']
        changed = True
    if disambig.subclass_type != disambig_json['subclass_type']:
        disambig.subclass_type = disambig_json['subclass_type']
        changed = True
    if disambig.obj_id != disambig_json['identifier']:
        disambig.obj_id = disambig_json['identifier']
        changed = True
    return changed

def convert_disambig(session_maker, backend, log, chunk_size):
    from model_perf_schema.core import Disambig
    
    log.info('convert_disambig')
    output_creator = OutputCreator(log)
    
    try:
        session = session_maker()
        
        min_disambig_id = 0
        max_disambig_id = 900000
        num_chunks = ceil(1.0*(max_disambig_id-min_disambig_id)/chunk_size)
        for i in range(0, num_chunks):
            min_id = min_disambig_id + i*chunk_size
            max_id = min_disambig_id + (i+1)*chunk_size
            
            #Grab old objects and current_objs
            if i < num_chunks-1:
                old_objs = session.query(Disambig).filter(Disambig.id >= min_id).filter(Disambig.id < max_id).all()
                new_objs = json.loads(backend.all_disambigs(min_id, min_id+chunk_size))
            else:
                old_objs = session.query(Disambig).filter(Disambig.id >= min_id).all()
                new_objs = json.loads(backend.all_disambigs(min_id, None))
                
            old_id_to_obj = dict([(x.id, x) for x in old_objs])
            new_id_to_obj = dict([(x['id'], x) for x in new_objs])
            
            old_ids = set(old_id_to_obj.keys())
            new_ids = set(new_id_to_obj.keys())
            
            #Inserts
            insert_ids = new_ids - old_ids
            for insert_id in insert_ids:
                session.add(create_disambig(new_id_to_obj[insert_id]))
            output_creator.num_added = output_creator.num_added + len(insert_ids)
               
            #Updates
            update_ids = new_ids & old_ids
            for update_id in update_ids:
                if update_disambig(new_id_to_obj[update_id], old_id_to_obj[update_id]):
                    output_creator.num_changed = output_creator.num_changed + 1
                
            #Deletes
            delete_ids = old_ids - new_ids
            for delete_id in delete_ids:
                session.delete(old_id_to_obj[delete_id])
            output_creator.num_removed = output_creator.num_removed + len(delete_ids)
            
        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            session.commit()
        
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()
        
    log.info('complete')

"""
--------------------- Convert Bioentity ---------------------
"""

def create_bioentity(bioentity_id, json_obj, locustabs_json):
    from model_perf_schema.core import Bioentity
    return Bioentity(bioentity_id, json_obj, locustabs_json)

def update_bioentity(json_obj, locustabs_json, bioentity):
    changed = False
    if bioentity.json != json_obj:
        bioentity.json = json_obj
        changed = True
    if bioentity.locustabs_json != locustabs_json:
        bioentity.locustabs_json = locustabs_json
        changed = True
    return changed

def convert_bioentity(session_maker, backend, log, chunk_size):
    from model_perf_schema.core import Bioentity
    
    log.info('convert_bioentity')
    output_creator = OutputCreator(log)
    
    try:
        session = session_maker()
        
        min_bioentity_id = 0
        max_bioentity_id = 10000
        num_chunks = ceil(1.0*(max_bioentity_id-min_bioentity_id)/chunk_size)
        for i in range(0, num_chunks):
            min_id = min_bioentity_id + i*chunk_size
            max_id = min_bioentity_id + (i+1)*chunk_size
            
            #Grab old objects and current_objs
            if i < num_chunks-1:
                old_objs = session.query(Bioentity).filter(Bioentity.id >= min_id).filter(Bioentity.id < max_id).all()
                new_json_objs = json.loads(backend.all_bioentities(min_id, min_id+chunk_size))
                new_locustab_json_objs = json.loads(backend.all_locustabs(min_id, min_id+chunk_size))
            else:
                old_objs = session.query(Bioentity).filter(Bioentity.id >= min_id).all()
                new_json_objs = json.loads(backend.all_bioentities(min_id, None))
                new_locustab_json_objs = json.loads(backend.all_locustabs(min_id, None))
                
            old_id_to_obj = dict([(x.id, x) for x in old_objs])
            new_id_to_json_obj = dict([(x['id'], json.dumps(x)) for x in new_json_objs])
            new_id_to_locustab_json_obj = dict([(x['id'], json.dumps(x)) for x in new_locustab_json_objs])
            
            old_ids = set(old_id_to_obj.keys())
            new_ids = set(new_id_to_json_obj.keys()) | set(new_id_to_locustab_json_obj.keys())
            
            #Inserts
            insert_ids = new_ids - old_ids
            for insert_id in insert_ids:
                json_obj = None if insert_id not in new_id_to_json_obj else new_id_to_json_obj[insert_id]
                locustab_json = None if insert_id not in new_id_to_locustab_json_obj else new_id_to_locustab_json_obj[insert_id]
                session.add(create_bioentity(insert_id, json_obj, locustab_json))
            output_creator.num_added = output_creator.num_added + len(insert_ids)
               
            #Updates
            update_ids = new_ids & old_ids
            for update_id in update_ids:
                json_obj = None if update_id not in new_id_to_json_obj else new_id_to_json_obj[update_id]
                locustab_json = None if update_id not in new_id_to_locustab_json_obj else new_id_to_locustab_json_obj[update_id]
                if update_bioentity(json_obj, locustab_json, old_id_to_obj[update_id]):
                    output_creator.changed(update_id, 'json')
                
            #Deletes
            delete_ids = old_ids - new_ids
            for delete_id in delete_ids:
                session.delete(old_id_to_obj[delete_id])
            output_creator.num_removed = output_creator.num_removed + len(delete_ids)
            
        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            session.commit()
        
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Bioconcept ---------------------
"""

def create_bioconcept(bioconcept_id, json_obj):
    from model_perf_schema.core import Bioconcept
    return Bioconcept(bioconcept_id, json_obj)

def update_bioconcept(json_obj, bioconcept):
    changed = False
    if bioconcept.json != json_obj:
        bioconcept.json = json_obj
        changed = True
    return changed

def convert_bioconcept(session_maker, backend, log, chunk_size):
    from model_perf_schema.core import Bioconcept
    
    log.info('convert_bioconcept')
    output_creator = OutputCreator(log)
    
    try:
        session = session_maker()
        
        min_bioconcept_id = 0
        max_bioconcept_id = 100000
        num_chunks = ceil(1.0*(max_bioconcept_id-min_bioconcept_id)/chunk_size)
        for i in range(0, num_chunks):
            min_id = min_bioconcept_id + i*chunk_size
            max_id = min_bioconcept_id + (i+1)*chunk_size
            
            #Grab old objects and current_objs
            if i < num_chunks-1:
                old_objs = session.query(Bioconcept).filter(Bioconcept.id >= min_id).filter(Bioconcept.id < max_id).all()
                new_json_objs = json.loads(backend.all_bioconcepts(min_id, min_id+chunk_size))
            else:
                old_objs = session.query(Bioconcept).filter(Bioconcept.id >= min_id).all()
                new_json_objs = json.loads(backend.all_bioconcepts(min_id, None))
                
            old_id_to_obj = dict([(x.id, x) for x in old_objs])
            new_id_to_json_obj = dict([(x['id'], json.dumps(x)) for x in new_json_objs])
            
            old_ids = set(old_id_to_obj.keys())
            new_ids = set(new_id_to_json_obj.keys())
            
            #Inserts
            insert_ids = new_ids - old_ids
            for insert_id in insert_ids:
                json_obj = None if insert_id not in new_id_to_json_obj else new_id_to_json_obj[insert_id]
                session.add(create_bioconcept(insert_id, json_obj))
            output_creator.num_added = output_creator.num_added + len(insert_ids)
               
            #Updates
            update_ids = new_ids & old_ids
            for update_id in update_ids:
                json_obj = None if update_id not in new_id_to_json_obj else new_id_to_json_obj[update_id]
                if update_bioconcept(json_obj, old_id_to_obj[update_id]):
                    output_creator.changed(update_id, 'json')
                
            #Deletes
            delete_ids = old_ids - new_ids
            for delete_id in delete_ids:
                session.delete(old_id_to_obj[delete_id])
            output_creator.num_removed = output_creator.num_removed + len(delete_ids)
            
        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            session.commit()
        
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Reference ---------------------
"""

def create_reference(bioentity_id, json_obj, bibentry):
    from model_perf_schema.core import Reference
    return Reference(bioentity_id, json_obj, bibentry)

def update_reference(json_obj, bibentry, reference):
    changed = False
    if reference.json != json_obj:
        reference.json = json_obj
        changed = True
    if reference.bibentry_json != bibentry:
        reference.bibentry_json = bibentry
        changed = True
    return changed

def convert_reference(session_maker, backend, log, chunk_size):
    from model_perf_schema.core import Reference
    
    log.info('convert_reference')
    output_creator = OutputCreator(log)
    
    try:
        session = session_maker()
        
        min_reference_id = 0
        max_reference_id = 100000
        num_chunks = ceil(1.0*(max_reference_id-min_reference_id)/chunk_size)
        for i in range(0, num_chunks):
            min_id = min_reference_id + i*chunk_size
            max_id = min_reference_id + (i+1)*chunk_size
            
            #Grab old objects and current_objs
            if i < num_chunks-1:
                old_objs = session.query(Reference).filter(Reference.id >= min_id).filter(Reference.id < max_id).all()
                new_json_objs = json.loads(backend.all_references(min_id, min_id+chunk_size))
                new_bibentry_objs = json.loads(backend.all_bibentries(min_id, min_id+chunk_size))
            else:
                old_objs = session.query(Reference).filter(Reference.id >= min_id).all()
                new_json_objs = json.loads(backend.all_references(min_id, None))
                new_bibentry_objs = json.loads(backend.all_bibentries(min_id, None))
                
            old_id_to_obj = dict([(x.id, x) for x in old_objs])
            new_id_to_json_obj = dict([(x['id'], backend.reference(int(x['id']), are_ids=False)) for x in new_json_objs])
            new_id_bibentry_obj = dict([(x['id'], json.dumps(x)) for x in new_bibentry_objs])
            
            old_ids = set(old_id_to_obj.keys())
            new_ids = set(new_id_to_json_obj.keys()) | set(new_id_bibentry_obj.keys())
            
            #Inserts
            insert_ids = new_ids - old_ids
            for insert_id in insert_ids:
                json_obj = None if insert_id not in new_id_to_json_obj else new_id_to_json_obj[insert_id]
                bibentry = None if insert_id not in new_id_bibentry_obj else new_id_bibentry_obj[insert_id]
                session.add(create_reference(insert_id, json_obj, bibentry))
            output_creator.num_added = output_creator.num_added + len(insert_ids)
               
            #Updates
            update_ids = new_ids & old_ids
            for update_id in update_ids:
                json_obj = None if update_id not in new_id_to_json_obj else new_id_to_json_obj[update_id]
                bibentry = None if update_id not in new_id_bibentry_obj else new_id_bibentry_obj[update_id]
                if update_reference(json_obj, bibentry, old_id_to_obj[update_id]):
                    output_creator.changed(update_id, 'json')
                
            #Deletes
            delete_ids = old_ids - new_ids
            for delete_id in delete_ids:
                session.delete(old_id_to_obj[delete_id])
            output_creator.num_removed = output_creator.num_removed + len(delete_ids)
            
        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            session.commit()
        
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()
        
    log.info('complete')

"""
--------------------- Convert Chemical ---------------------
"""

def create_chemical(chemical_id, json_obj):
    from model_perf_schema.core import Chemical
    return Chemical(chemical_id, json_obj)

def update_chemical(json_obj, chemical):
    changed = False
    if chemical.json != json_obj:
        chemical.json = json_obj
        changed = True
    return changed

def convert_chemical(session_maker, backend, log, chunk_size):
    from model_perf_schema.core import Chemical

    log.info('convert_chemical')
    output_creator = OutputCreator(log)

    try:
        session = session_maker()

        min_chemical_id = 0
        max_chemical_id = 50000
        num_chunks = ceil(1.0*(max_chemical_id-min_chemical_id)/chunk_size)
        for i in range(0, num_chunks):
            min_id = min_chemical_id + i*chunk_size
            max_id = min_chemical_id + (i+1)*chunk_size

            #Grab old objects and current_objs
            if i < num_chunks-1:
                old_objs = session.query(Chemical).filter(Chemical.id >= min_id).filter(Chemical.id < max_id).all()
                new_json_objs = json.loads(backend.all_chemicals(min_id, min_id+chunk_size))
            else:
                old_objs = session.query(Chemical).filter(Chemical.id >= min_id).all()
                new_json_objs = json.loads(backend.all_chemicals(min_id, None))

            old_id_to_obj = dict([(x.id, x) for x in old_objs])
            new_id_to_json_obj = dict([(x['id'], json.dumps(x)) for x in new_json_objs])

            old_ids = set(old_id_to_obj.keys())
            new_ids = set(new_id_to_json_obj.keys())

            #Inserts
            insert_ids = new_ids - old_ids
            for insert_id in insert_ids:
                json_obj = None if insert_id not in new_id_to_json_obj else new_id_to_json_obj[insert_id]
                session.add(create_chemical(insert_id, json_obj))
            output_creator.num_added = output_creator.num_added + len(insert_ids)

            #Updates
            update_ids = new_ids & old_ids
            for update_id in update_ids:
                json_obj = None if update_id not in new_id_to_json_obj else new_id_to_json_obj[update_id]
                if update_chemical(json_obj, old_id_to_obj[update_id]):
                    output_creator.changed(update_id, 'json')

            #Deletes
            delete_ids = old_ids - new_ids
            for delete_id in delete_ids:
                session.delete(old_id_to_obj[delete_id])
            output_creator.num_removed = output_creator.num_removed + len(delete_ids)


            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            session.commit()


    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()

    log.info('complete')

"""
--------------------- Convert Author ---------------------
"""

def create_author(author_id, json_obj):
    from model_perf_schema.core import Author
    return Author(author_id, json_obj)

def update_author(json_obj, author):
    changed = False
    if author.json != json_obj:
        author.json = json_obj
        changed = True
    return changed

def convert_author(session_maker, backend, log, chunk_size):
    from model_perf_schema.core import Author

    log.info('convert_author')
    output_creator = OutputCreator(log)

    try:
        session = session_maker()

        #Grab old objects and current_objs
        old_objs = session.query(Author).all()
        new_json_objs = json.loads(backend.all_authors(None, None))

        old_id_to_obj = dict([(x.id, x) for x in old_objs])
        new_id_to_json_obj = dict([(x['id'], json.dumps(x)) for x in new_json_objs])

        old_ids = set(old_id_to_obj.keys())
        new_ids = set(new_id_to_json_obj.keys())

        #Inserts
        insert_ids = new_ids - old_ids
        for insert_id in insert_ids:
            json_obj = None if insert_id not in new_id_to_json_obj else new_id_to_json_obj[insert_id]
            session.add(create_author(insert_id, json_obj))
        output_creator.num_added = output_creator.num_added + len(insert_ids)

        #Updates
        update_ids = new_ids & old_ids
        for update_id in update_ids:
            json_obj = None if update_id not in new_id_to_json_obj else new_id_to_json_obj[update_id]
            if update_author(json_obj, old_id_to_obj[update_id]):
                output_creator.changed(update_id, 'json')

        #Deletes
        delete_ids = old_ids - new_ids
        for delete_id in delete_ids:
            session.delete(old_id_to_obj[delete_id])
        output_creator.num_removed = output_creator.num_removed + len(delete_ids)


        output_creator.finished()
        session.commit()


    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()

    log.info('complete')

"""
--------------------- Convert Ontology ---------------------
"""

def create_ontology(class_type, json_obj):
    from model_perf_schema.core import Ontology
    return Ontology(class_type, json_obj)

def update_ontology(json_obj, ontology):
    changed = False
    if ontology.json != json_obj:
        ontology.json = json_obj
        changed = True
    return changed

def convert_ontology(session_maker, backend, log, chunk_size):
    from model_perf_schema.core import Ontology

    log.info('convert_ontology')
    output_creator = OutputCreator(log)

    try:
        session = session_maker()

        #Grab old objects and current_objs
        phenotype_ontology = backend.phenotype_ontology()

        old_type_to_obj = dict([(x.class_type, x) for x in session.query(Ontology).all()])
        new_type_to_json_obj = {'PHENOTYPE': phenotype_ontology}

        old_types = set(old_type_to_obj.keys())
        new_types = set(new_type_to_json_obj.keys())

        #Inserts
        insert_ids = new_types - old_types
        for insert_id in insert_ids:
            json_obj = None if insert_id not in new_type_to_json_obj else new_type_to_json_obj[insert_id]
            session.add(create_ontology(insert_id, json_obj))
        output_creator.num_added = output_creator.num_added + len(insert_ids)

        #Updates
        update_ids = new_types & old_types
        for update_id in update_ids:
            json_obj = None if update_id not in new_type_to_json_obj else new_type_to_json_obj[update_id]
            if update_author(json_obj, old_type_to_obj[update_id]):
                output_creator.changed(update_id, 'json')

        #Deletes
        delete_ids = old_types - new_types
        for delete_id in delete_ids:
            session.delete(old_type_to_obj[delete_id])
        output_creator.num_removed = output_creator.num_removed + len(delete_ids)


        output_creator.finished()
        session.commit()


    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()

    log.info('complete')