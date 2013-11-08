'''
Created on Oct 25, 2013

@author: kpaskov
'''
from convert_utils import create_or_update
from convert_utils.output_manager import OutputCreator
import logging
import sys

"""
--------------------- Convert Phenotype ---------------------
"""

def create_phenotype_type(observable):
    if observable in {'chemical compound accumulation', 'resistance to chemicals', 'osmotic stress resistance', 'alkaline pH resistance',
                      'ionic stress resistance', 'oxidative stress resistance', 'small molecule transport', 'metal resistance', 
                      'acid pH resistance', 'hyperosmotic stress resistance', 'hypoosmotic stress resistance', 'chemical compound excretion'}:
        return 'chemical'
    elif observable in {'protein/peptide accumulation', 'protein/peptide modification', 'protein/peptide distribution', 
                        'RNA accumulation', 'RNA localization', 'RNA modification'}:
        return 'pp_rna'
    else:
        return 'cellular'

def create_phenotype(old_phenotype, key_to_source):
    from model_new_schema.bioconcept import Phenotype as NewPhenotype
    observable = old_phenotype.observable
    qualifier = old_phenotype.qualifier
    mutant_type = old_phenotype.mutant_type
    
    source = key_to_source['SGD']
    phenotype_type = create_phenotype_type(old_phenotype.observable)
    new_phenotype = NewPhenotype(source, None, None,
                                 observable, qualifier, mutant_type, phenotype_type,
                                 old_phenotype.date_created, old_phenotype.created_by)
    return [new_phenotype]

def create_phenotype_from_cv_term(old_cvterm, key_to_source):
    from model_new_schema.bioconcept import Phenotype as NewPhenotype
    observable = old_cvterm.name
    source = key_to_source['SGD']
    phenotype_type = create_phenotype_type(observable)
    new_phenotype = NewPhenotype(source, None, None,
                                 observable, None, None, phenotype_type,
                                 old_cvterm.date_created, old_cvterm.created_by)
    return [new_phenotype]

def convert_phenotype(old_session_maker, new_session_maker):
    from model_new_schema.bioconcept import Phenotype as NewPhenotype
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.phenotype import Phenotype as OldPhenotype
    from model_old_schema.cv import CVTerm as OldCVTerm
    
    log = logging.getLogger('convert.bioconcept.phenotype')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()     
        
        #Grab all current objects
        current_objs = new_session.query(NewPhenotype).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs]) 
                  
        #Values to check
        values_to_check = ['observable', 'qualifier', 'mutant_type', 'phenotype_type', 'display_name', 'description', 'source_id', 'link', 'sgdid']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        keys_already_seen = set()
        
        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
            
        #Grab old objects
        old_objs = old_session.query(OldPhenotype).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_phenotype(old_obj, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    keys_already_seen.add(key)
                    
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)
         
        #Convert cv terms           
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no == 6).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_phenotype_from_cv_term(old_obj, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
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
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')
    
"""
--------------------- Convert GO ---------------------
"""

abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}
def create_go(old_go, key_to_source):
    from model_new_schema.bioconcept import Go as NewGo
    
    display_name = old_go.go_term
    source = key_to_source['GO']
    new_go = NewGo(display_name, source, None, old_go.go_definition,
                   old_go.go_go_id, abbrev_to_go_aspect[old_go.go_aspect],  
                   old_go.date_created, old_go.created_by)
    return [new_go]

def convert_go(old_session_maker, new_session_maker):
    from model_new_schema.bioconcept import Go as NewGo
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.go import Go as OldGo
    
    log = logging.getLogger('convert.bioconcept.go')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()     
        
        #Grab all current objects
        current_objs = new_session.query(NewGo).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs]) 
                  
        #Values to check
        values_to_check = ['go_id', 'go_aspect', 'display_name', 'link', 'sgdid', 'description', 'source_id']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
                
        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
            
        #Grab old objects
        old_objs = old_session.query(OldGo).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_go(old_obj, key_to_source)
                
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
--------------------- Convert EC ---------------------
"""

def create_ecnumber(old_dbxref, key_to_source):
    from model_new_schema.bioconcept import ECNumber as NewECNumber
    
    display_name = old_dbxref.dbxref_id
    source = key_to_source[old_dbxref.source]

    return [NewECNumber(display_name, source, old_dbxref.dbxref_name, old_dbxref.date_created, old_dbxref.created_by)]

def convert_ecnumber(old_session_maker, new_session_maker):
    from model_new_schema.bioconcept import ECNumber as NewECNumber
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.general import Dbxref as OldDbxref
    
    log = logging.getLogger('convert.bioconcept.ecnumber')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()     
        
        #Grab all current objects
        current_objs = new_session.query(NewECNumber).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs]) 
                  
        #Values to check
        values_to_check = ['display_name', 'link', 'sgdid', 'description', 'source_id']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
                
        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
            
        #Grab old objects
        old_objs = old_session.query(OldDbxref).filter(OldDbxref.dbxref_type == 'EC number').all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_ecnumber(old_obj, key_to_source)
                
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
---------------------Convert------------------------------
"""  

def convert(old_session_maker, new_session_maker):
    convert_phenotype(old_session_maker, new_session_maker)
    
    convert_go(old_session_maker, new_session_maker)
    
    convert_ecnumber(old_session_maker, new_session_maker)
    
