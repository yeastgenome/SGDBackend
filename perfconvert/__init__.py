'''
Created on Sep 25, 2013

@author: kpaskov
'''
from backend import prepare_sgdbackend
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from perfconvert_utils import set_up_logging, prepare_connections
from sqlalchemy.sql.expression import select
from threading import Thread
import json
import logging
import sys

def convert_obj(engine, table, id_column_name, link, chunk_size, min_id, label):
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        current_id_to_json = {}
        new_id_to_json = {}
        finished = False
        while not finished:
            new_ids = set(new_id_to_json.keys())
            current_ids = set(current_id_to_json.keys())
            
            #Inserts
            inserts = [{id_column_name: x, 'json': new_id_to_json[x]} for x in new_ids - current_ids]
            if len(inserts) > 0:
                engine.execute(table.insert(), inserts)
            output_creator.num_added = output_creator.num_added + len(inserts)
            
            #Deletes
            deletes = current_ids - new_ids
            if len(deletes) > 0:
                engine.execute(table.delete().where(getattr(table.c, id_column_name).in_(deletes)))
            output_creator.num_removed = output_creator.num_removed + len(deletes)
            
            #Updates
            updates = current_ids & new_ids
            for obj_id in updates:
                current_json = current_id_to_json[obj_id]
                new_json = new_id_to_json[obj_id]
                
                if current_json != new_json:
                    engine.execute(table.update().where(getattr(table.c, id_column_name) == obj_id).values(json=new_json))
                    output_creator.changed(obj_id, 'json')
                        
            #Get ready for next round.
            current_objs = engine.execute(select([table]).where(getattr(table.c, id_column_name) >= min_id).where(getattr(table.c, id_column_name) < min_id + chunk_size)).fetchall()
            current_id_to_json = dict([(getattr(x, id_column_name), x.json) for x in current_objs])
            new_objs = json.loads(link(min_id, min_id+chunk_size))
            new_id_to_json = dict([(x['id'], json.dumps(x)) for x in new_objs])
            min_id = min_id+chunk_size
            if len(new_objs) == 0:
                finished = True
            
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
        
    output_creator.finished()
    
def convert_obj_by_bioentity(engine, table, link, bioent_ids, chunk_size, label):
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        current_id_to_json = {}
        new_ids = set()
        min_id = 0
        finished = False
        while not finished:
            current_ids = set(current_id_to_json.keys())
            
            #Inserts
            inserts = [{'bioentity_id': x, 'json': link(str(x))} for x in new_ids - current_ids]
            if len(inserts) > 0:
                engine.execute(table.insert(), inserts)
            output_creator.num_added = output_creator.num_added + len(inserts)
            
            #Deletes
            deletes = current_ids - new_ids
            if len(deletes) > 0:
                engine.execute(table.delete().where(table.c.bioentity_id.in_(deletes)))
            output_creator.num_removed = output_creator.num_removed + len(deletes)
            
            #Updates
            updates = current_ids & new_ids
            for obj_id in updates:
                current_json = current_id_to_json[obj_id]
                new_json = link(str(obj_id))
                
                if current_json != new_json:
                    engine.execute(table.update().where(table.c.bioentity_id == obj_id).values(json=new_json))
                    output_creator.changed(obj_id, 'json')
                        
            #Get ready for next round.
            current_objs = engine.execute(select([table]).where(table.c.bioentity_id >= min_id).where(table.c.bioentity_id < min_id + chunk_size)).fetchall()
            current_id_to_json = dict([(x.bioentity_id, x.json) for x in current_objs])
            new_ids = set([x for x in bioent_ids if x >= min_id and x < min_id+chunk_size])
            min_id = min_id+chunk_size
            if len(new_ids) == 0:
                finished = True
                
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
        
    output_creator.finished()
    
def convert_disambigs(engine, table, link, chunk_size, label):
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        current_id_to_data = {}
        new_id_to_data = {}
        finished = False
        min_id = 0
        while not finished:
            new_ids = set(new_id_to_data.keys())
            current_ids = set(current_id_to_data.keys())
            
            #Inserts
            inserts = [{'disambig_id': x, 
                        'disambig_key': new_id_to_data[x][0], 
                        'class_type':new_id_to_data[x][1], 
                        'subclass_type':new_id_to_data[x][2], 
                        'identifier':new_id_to_data[x][3]} for x in new_ids - current_ids]
            if len(inserts) > 0:
                engine.execute(table.insert(), inserts)
            output_creator.num_added = output_creator.num_added + len(inserts)
            
            #Deletes
            deletes = current_ids - new_ids
            if len(deletes) > 0:
                engine.execute(table.delete().where(getattr(table.c, 'disambig_id').in_(deletes)))
            output_creator.num_removed = output_creator.num_removed + len(deletes)
            
            #Updates
            updates = current_ids & new_ids
            for obj_id in updates:
                current_data = current_id_to_data[obj_id]
                new_data = new_id_to_data[obj_id]
                if current_data != new_data:
                    engine.execute(table.update().where(table.c.disambig_id == obj_id).values(disambig_key=new_data[0], class_type=new_data[1], subclass_type=new_data[2], identifier=new_data[3]))
                    output_creator.changed(obj_id, 'json')
            #output_creator.finished()
                        
            #Get ready for next round.
            current_objs = engine.execute(select([table]).where(table.c.disambig_id >= min_id).where(table.c.disambig_id < min_id + chunk_size)).fetchall()
            current_id_to_data = dict([(x.disambig_id, (x.disambig_key, x.class_type, x.subclass_type, x.identifier)) for x in current_objs])
            new_objs = json.loads(link(min_id, min_id+chunk_size))
            new_id_to_data = dict([(x['id'], (x['disambig_key'], x['class_type'], x['subclass_type'], x['identifier'])) for x in new_objs])
            min_id = min_id+chunk_size
            if len(new_objs) == 0:
                finished = True
    
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
        
    output_creator.finished()
  
"""
---------------------Convert------------------------------
"""  

def convert(engine, meta):
    log = set_up_logging('convert.performance')
    
    log.info('load_sgdbackend')
    backend = prepare_sgdbackend()[0]
    log.info('begin')
    ################# Core Converts ###########################
#    #Bioentity
#    convert_obj(engine, meta.tables['bioentity'], 'bioentity_id', backend.all_bioentities, 1000, 0, 'convert.performance.bioentity')
#    
#    #Reference
#    convert_obj(engine, meta.tables['reference'], 'reference_id', backend.all_references, 10000, 0, 'convert.performance.reference')
#    
#    #Bioconcept
    convert_obj(engine, meta.tables['bioconcept'], 'bioconcept_id', backend.all_bioconcepts, 50000000, 10000000, 'convert.performance.bioconcept')
#
#    #Disambigs
#    convert_disambigs(engine, meta.tables['disambig'], backend.all_disambigs, 1000, 'convert.performance.disambigs')
#    ################# Converts in parallel ###########################
#    
    #Get bioents
    bioent_ids = [bioent.bioentity_id for bioent in engine.execute(select([meta.tables['bioentity']])).fetchall()]
#    
#    #Bibentry
#    try:
#        convert_obj(engine, meta.tables['reference_bibentry'], 'reference_id', backend.all_bibentries, 1000, 0, 'convert.performance.bibentry')
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#    
#    #Bioentitytabs
#    try:
#        convert_obj_by_bioentity(engine, meta.tables['locustabs'], backend.locustabs, bioent_ids, 1000, 'convert.performance.locustabs')
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#    
#    #Interaction section
#    try:
#        convert_obj_by_bioentity(engine, meta.tables['interaction_overview'], backend.interaction_overview, bioent_ids, 1000, 'convert.performance.interaction_overview')
#        convert_obj_by_bioentity(engine, meta.tables['interaction_details'], backend.interaction_details, bioent_ids, 1000, 'convert.performance.interaction_details')
#        convert_obj_by_bioentity(engine, meta.tables['interaction_graph'], backend.interaction_graph, bioent_ids, 1000, 'convert.performance.interaction_graph')
#        convert_obj_by_bioentity(engine, meta.tables['interaction_resources'], backend.interaction_resources, bioent_ids, 1000, 'convert.performance.interaction_resources')
#        convert_obj_by_bioentity(engine, meta.tables['interaction_references'], backend.interaction_references, bioent_ids, 1000, 'convert.performance.interaction_references')
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    #Literature section
    try:
        convert_obj_by_bioentity(engine, meta.tables['literature_overview'], backend.literature_overview, bioent_ids, 1000, 'convert.performance.literature_overview')
        convert_obj_by_bioentity(engine, meta.tables['literature_details'], backend.literature_details, bioent_ids, 1000, 'convert.performance.literature_details')
        convert_obj_by_bioentity(engine, meta.tables['literature_graph'], backend.literature_graph, bioent_ids, 1000, 'convert.performance.literature_graph')
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#    
#    #Regulation section
#    try:
#        convert_obj_by_bioentity(engine, meta.tables['regulation_overview'], backend.regulation_overview, bioent_ids, 1000, 'convert.performance.regulation_overview')
#        convert_obj_by_bioentity(engine, meta.tables['regulation_details'], backend.regulation_details, bioent_ids, 1000, 'convert.performance.regulation_details')
#        convert_obj_by_bioentity(engine, meta.tables['regulation_graph'], backend.regulation_graph, bioent_ids, 1000, 'convert.performance.regulation_graph')
#        convert_obj_by_bioentity(engine, meta.tables['regulation_references'], backend.regulation_references, bioent_ids, 1000, 'convert.performance.regulation_references')
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#    
#    #Phenotype section
#    try:
#        convert_obj_by_bioentity(engine, meta.tables['phenotype_references'], backend.phenotype_references, bioent_ids, 1000, 'convert.performance.phenotype_references')
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#    
#    #Go section
#    try:
#        convert_obj_by_bioentity(engine, meta.tables['go_references'], backend.go_references, bioent_ids, 1000, 'convert.performance.go_references')
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#   
#    #Protein section
#    try:
#        convert_obj_by_bioentity(engine, meta.tables['protein_domain_details'], backend.protein_domain_details, bioent_ids, 1000, 'convert.performance.protein_domain_details')
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#    
#    #Misc
#    try:
#        convert_obj_by_bioentity(engine, meta.tables['binding_site_details'], backend.binding_site_details, bioent_ids, 1000, 'convert.performance.binding_site_details')
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )

if __name__ == "__main__":
    engine, meta = prepare_connections()
    convert(engine, meta)
    
    