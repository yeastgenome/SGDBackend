'''
Created on Oct 25, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, set_up_logging, prepare_connections, \
    create_format_name
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.sql.expression import distinct
import logging
import sys

"""
--------------------- Convert Phenotype Bioitems ---------------------
"""

def create_phenotype_bioitems(old_phenotype_feature, key_to_source):
    from model_new_schema.bioitem import Allele as NewAllele, Proteinbioitem as NewProteinbioitem
    
    allele_reporters = []
    if old_phenotype_feature.experiment is not None:
        allele_info = old_phenotype_feature.experiment.allele
        if allele_info is not None:
            source = key_to_source['SGD']
            new_allele = NewAllele(allele_info[0], source, allele_info[1])
            allele_reporters.append(new_allele)
        reporter_info = old_phenotype_feature.experiment.reporter
        if reporter_info is not None:
            source = key_to_source['SGD']
            new_reporter = NewProteinbioitem(reporter_info[0], source, reporter_info[1])
            allele_reporters.append(new_reporter)
    return allele_reporters

def convert_phenotype_bioitems(old_session_maker, new_session_maker):
    from model_new_schema.bioitem import Allele as NewAllele, Proteinbioitem as NewProteinbioitem
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.phenotype import PhenotypeFeature as OldPhenotypeFeature
    
    log = logging.getLogger('convert.bioitem.phenotype_bioitems')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()     
        
        #Grab all current objects
        current_objs = new_session.query(NewAllele).all()
        current_objs.extend(new_session.query(NewProteinbioitem).all())
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs]) 
                  
        #Values to check
        values_to_check = ['description', 'display_name', 'source_id', 'link']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        keys_already_seen = set()
        
        #Grab cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
            
        #Grab old objects
        old_objs = old_session.query(OldPhenotypeFeature).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_phenotype_bioitems(old_obj, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if key not in key_to_current_obj else key_to_current_obj[key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    keys_already_seen.add(key)
                    
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)
                        
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    output_creator.finished()
    
"""
--------------------- Convert Go Bioitems ---------------------
"""

dbxref_type_to_class = {
                        'DNA accession ID': 'DNA',
                        'Gene ID': 'DNA',
                        'HAMAP ID': 'PROTEIN',
                        'InterPro': 'PROTEIN',
                        'PANTHER': 'PROTEIN',
                        'PDB identifier': 'PROTEIN',
                        'Protein version ID': 'PROTEIN',
                        'UniPathway ID': 'PATHWAY',
                        'UniProt/Swiss-Prot ID': 'PROTEIN',
                        'UniProtKB Keyword': 'PROTEIN',
                        'UniProtKB Subcellular Location': 'PROTEIN'
                        }

def create_go_bioitems(old_dbxref, key_to_source):
    from model_new_schema.bioitem import Bioitem as NewBioitem
    dbxref_type = old_dbxref.dbxref_type
    if dbxref_type != 'GOID' and dbxref_type != 'EC number' and dbxref_type != 'DBID Primary':
        class_type = dbxref_type_to_class[dbxref_type]
        source_key = create_format_name(old_dbxref.source)
        source = None if source_key not in key_to_source else key_to_source[source_key]
        if source is None:
            print source_key
            return []
        link = None
        if dbxref_type == 'UniProt/Swiss-Prot ID':
            urls = old_dbxref.urls
            if len(urls) == 1:
                link = urls[0].url.replace('_SUBSTITUTE_THIS_', old_dbxref.dbxref_id)
        return [NewBioitem(old_dbxref.dbxref_id, old_dbxref.dbxref_id, class_type, link, source, old_dbxref.dbxref_name)]
        
    return []

def convert_go_bioitems(old_session_maker, new_session_maker):
    from model_new_schema.bioitem import Bioitem as NewBioitem
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.go import GorefDbxref as OldGorefDbxref
    from model_old_schema.general import Dbxref as OldDbxref
    
    log = logging.getLogger('convert.bioitem.go_bioitems')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()     
        
        #Grab all current objects
        current_objs = new_session.query(NewBioitem).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs]) 
                  
        #Values to check
        values_to_check = ['description', 'display_name', 'source_id', 'link']
                        
        keys_already_seen = set()
        
        #Grab cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
            
        #Grab old objects
        dbxref_ids = [x[0] for x in old_session.query(distinct(OldGorefDbxref.dbxref_id)).all()]
        num_chunks = ceil(1.0*len(dbxref_ids)/500)
        old_objs = []
        for i in range(num_chunks):
            dbxref_id_chunk = dbxref_ids[i*500: (i+1)*500]
            old_objs.extend(old_session.query(OldDbxref).filter(OldDbxref.id.in_(dbxref_id_chunk)).all())
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_go_bioitems(old_obj, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if key not in key_to_current_obj else key_to_current_obj[key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    keys_already_seen.add(key)

        #Commit
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    output_creator.finished()
    
"""
---------------------Convert------------------------------
"""  

def convert(old_session_maker, new_session_maker):
    log = set_up_logging('convert.bioitems')
    
    log.info('begin')
            
    convert_phenotype_bioitems(old_session_maker, new_session_maker)
    
    convert_go_bioitems(old_session_maker, new_session_maker)
    
if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)
    