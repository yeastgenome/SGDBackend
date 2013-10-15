'''
Created on Sep 25, 2013

@author: kpaskov
'''
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from perfconvert_utils import create_or_update, set_up_logging, \
    prepare_connections, get_json, get_json_str
from perfconvert_utils.link_maker import all_bioentity_link, all_reference_link, \
    interaction_overview_link, interaction_details_link, interaction_graph_link, \
    interaction_resources_link, interaction_references_link, \
    literature_overview_link, literature_details_link, literature_graph_link, \
    regulation_overview_link, regulation_details_link, regulation_references_link, \
    phenotype_references_link, go_references_link, binding_site_details_link, \
    protein_domain_details_link, all_bibentry_link, regulation_graph_link, \
    all_bioconcept_link, locustabs_link
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
            output_creator.finished()
                        
            #Get ready for next round.
            current_objs = engine.execute(select([table]).where(getattr(table.c, id_column_name) >= min_id).where(getattr(table.c, id_column_name) < min_id + chunk_size)).fetchall()
            current_id_to_json = dict([(getattr(x, id_column_name), x.json) for x in current_objs])
            new_objs = get_json(link(min_id, min_id+chunk_size))
            new_id_to_json = dict([(x['id'], json.dumps(x)) for x in new_objs])
            min_id = min_id+chunk_size
            if len(new_objs) == 0:
                finished = True
            
           
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
        
    log.info('complete')
    
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
            inserts = [{'bioentity_id': x, 'json': get_json_str(link(str(x)))} for x in new_ids - current_ids]
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
                new_json = get_json_str(link(str(obj_id)))
                
                if current_json != new_json:
                    engine.execute(table.update().where(table.c.bioentity_id == obj_id).values(json=new_json))
                    output_creator.changed(obj_id, 'json')
            output_creator.finished()
                        
            #Get ready for next round.
            current_objs = engine.execute(select([table]).where(table.c.bioentity_id >= min_id).where(table.c.bioentity_id < min_id + chunk_size)).fetchall()
            current_id_to_json = dict([(x.bioentity_id, x.json) for x in current_objs])
            new_ids = set([x for x in bioent_ids if x >= min_id and x < min_id+chunk_size])
            min_id = min_id+chunk_size
            if len(new_ids) == 0:
                finished = True
            
           
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
        
    log.info('complete')
  
"""
---------------------Convert------------------------------
"""  

def convert(engine, meta):
    log = set_up_logging('convert.performance')
    log.info('begin')
        
    ################# Core Converts ###########################
    #Bioentity
    convert_obj(engine, meta.tables['bioentity'], 'bioentity_id', all_bioentity_link, 1000, 0, 'convert.performance.bioentity')
    
    #Reference
    convert_obj(engine, meta.tables['reference'], 'reference_id', all_reference_link, 10000, 0, 'convert.performance.reference')
    
    #Bioconcept
    #convert_obj(engine, meta.tables['bioconcept'], 'bioconcept_id', all_bioconcept_link, 1000, 50000000, 'convert.performance.bioconcept')
    convert_obj(engine, meta.tables['bioconcept'], 'bioconcept_id', all_bioconcept_link, 1000, 60003000, 'convert.performance.bioconcept')

    ################# Converts in parallel ###########################
    
    #Get bioents
    bioent_ids = [bioent.bioentity_id for bioent in engine.execute(select([meta.tables['bioentity']])).fetchall()]
    
    #Bibentry
    try:
        convert_obj(engine, meta.tables['reference_bibentry'], 'reference_id', all_bibentry_link, 1000, 0, 'convert.performance.bibentry')
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    #Bioentitytabs
    class ConvertLocustabsThread (Thread):
        def run(self):
            try:
                convert_obj_by_bioentity(engine, meta.tables['locustabs'], locustabs_link, bioent_ids, 1000, 'convert.performance.locustabs')
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertLocustabsThread().start()
    
    #Interaction section
    class ConvertInteractionSectionThread (Thread):
        def run(self):
            try:
                convert_obj_by_bioentity(engine, meta.tables['interaction_overview'], interaction_overview_link, bioent_ids, 1000, 'convert.performance.interaction_overview')
                convert_obj_by_bioentity(engine, meta.tables['interaction_details'], interaction_details_link, bioent_ids, 1000, 'convert.performance.interaction_details')
                convert_obj_by_bioentity(engine, meta.tables['interaction_graph'], interaction_graph_link, bioent_ids, 1000, 'convert.performance.interaction_graph')
                convert_obj_by_bioentity(engine, meta.tables['interaction_resources'], interaction_resources_link, bioent_ids, 1000, 'convert.performance.interaction_resources')
                convert_obj_by_bioentity(engine, meta.tables['interaction_references'], interaction_resources_link, bioent_ids, 1000, 'convert.performance.interaction_references')
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertInteractionSectionThread().start()
    
    #Literature section
    class ConvertLiteratureSectionThread (Thread):
        def run(self):
            try:
                convert_obj_by_bioentity(engine, meta.tables['literature_overview'], literature_overview_link, bioent_ids, 1000, 'convert.performance.literature_overview')
                convert_obj_by_bioentity(engine, meta.tables['literature_details'], literature_details_link, bioent_ids, 1000, 'convert.performance.literature_details')
                convert_obj_by_bioentity(engine, meta.tables['literature_graph'], literature_graph_link, bioent_ids, 1000, 'convert.performance.literature_graph')
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertLiteratureSectionThread().start()
    
    #Regulation section
    class ConvertRegulationSectionThread (Thread):
        def run(self):
            try:
                convert_obj_by_bioentity(engine, meta.tables['regulation_overview'], regulation_overview_link, bioent_ids, 1000, 'convert.performance.regulation_overview')
                convert_obj_by_bioentity(engine, meta.tables['regulation_details'], regulation_details_link, bioent_ids, 1000, 'convert.performance.regulation_details')
                convert_obj_by_bioentity(engine, meta.tables['regulation_graph'], regulation_graph_link, bioent_ids, 1000, 'convert.performance.regulation_graph')
                convert_obj_by_bioentity(engine, meta.tables['regulation_references'], regulation_graph_link, bioent_ids, 1000, 'convert.performance.regulation_references')
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertRegulationSectionThread().start()
    
    #Phenotype section
    class ConvertPhenotypeSectionThread (Thread):
        def run(self):
            try:
                convert_obj_by_bioentity(engine, meta.tables['phenotype_references'], phenotype_references_link, bioent_ids, 1000, 'convert.performance.phenotype_references')
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertPhenotypeSectionThread().start()
    
    #Go section
    class ConvertGoSectionThread (Thread):
        def run(self):
            try:
                convert_obj_by_bioentity(engine, meta.tables['go_references'], go_references_link, bioent_ids, 1000, 'convert.performance.go_references')
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertGoSectionThread().start()
   
    #Protein section
    class ConvertProteinSectionThread (Thread):
        def run(self):
            try:
                convert_obj_by_bioentity(engine, meta.tables['protein_domain_details'], protein_domain_details_link, bioent_ids, 1000, 'convert.performance.protein_domain_details')
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertProteinSectionThread().start()
    
    #Misc
    class ConvertMiscThread (Thread):
        def run(self):
            try:
                convert_obj_by_bioentity(engine, meta.tables['binding_site_details'], binding_site_details_link, bioent_ids, 1000, 'convert.performance.binding_site_details')
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertMiscThread().start()

if __name__ == "__main__":
    engine, meta = prepare_connections()
    convert(engine, meta)
    
    