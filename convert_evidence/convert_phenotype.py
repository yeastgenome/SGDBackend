'''
Created on May 6, 2013

@author: kpaskov
'''
from convert_aux.convert_aux_other import convert_bioentity_reference, \
    convert_disambigs
from convert_utils import set_up_logging, create_or_update, create_format_name, \
    prepare_connections
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
import logging
import sys

'''
 This code is used to convert phenotype data from the old schema to the new. It does this by
 creating new schema objects from the old, then comparing these new objects to those already
 stored in the new database. If a newly created object matches one that is already stored, the two
 are compared and the database fields are updated. If a newly created object does not match one that is 
 already stored, it is added to the database.
'''
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
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    observable = old_phenotype.observable
    qualifier = old_phenotype.qualifier
    mutant_type = old_phenotype.mutant_type
    
    source = key_to_source['SGD']
    new_phenotype = NewPhenotype(source, None, None,
                                 observable, qualifier, mutant_type, 
                                 create_phenotype_type(old_phenotype.observable),
                                 old_phenotype.date_created, old_phenotype.created_by)
    return [new_phenotype]

def convert_phenotype(old_session_maker, new_session_maker):
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    from model_new_schema.evelement import Source as NewSource
    from model_old_schema.phenotype import Phenotype as OldPhenotype
    
    log = logging.getLogger('convert.phenotype.phenotype')
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
--------------------- Convert Evidence ---------------------
"""

def create_evidence(old_phenotype_feature, key_to_reflink, key_to_phenotype, 
                         id_to_reference, id_to_bioentity, key_to_strain, key_to_experiment, 
                         key_to_allele, key_to_chemical, key_to_source):
    from model_new_schema.phenotype import Phenotypeevidence as NewPhenotypeevidence, create_phenotype_format_name

    reference_id = key_to_reflink[('PHENO_ANNOTATION_NO', old_phenotype_feature.id)].reference_id
    reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
    bioent_id = old_phenotype_feature.feature_id
    bioentity = None if bioent_id not in id_to_bioentity else id_to_bioentity[bioent_id]
    
    phenotype_key = (create_phenotype_format_name(old_phenotype_feature.observable, old_phenotype_feature.qualifier, old_phenotype_feature.mutant_type), 'PHENOTYPE')
    phenotype = None if phenotype_key not in key_to_phenotype else key_to_phenotype[phenotype_key]
       
    experiment_key = create_format_name(old_phenotype_feature.experiment_type)
    experiment = None if experiment_key not in key_to_experiment else key_to_experiment[experiment_key]

    strain = None
    note = None
    conditions = []
       
    old_experiment = old_phenotype_feature.experiment                                 
    if old_experiment is not None:
        #Create note
        note_pieces = []
        if old_experiment.experiment_comment is not None:
            note_pieces.append(old_experiment.experiment_comment)
        for (a, b) in old_experiment.details:
            note_pieces.append(a if b is None else a + ': ' + b)
        
        strain_details = None if old_experiment.strain == None else old_experiment.strain[1]
        if strain_details is not None:
            note_pieces.append(strain_details)
            
        for (a, b) in old_experiment.details:
            note_pieces.append(a if b is None else a + ': ' + b)
        note = '; '.join(note_pieces)
            
        #Get strain
        strain_key = None if old_experiment.strain == None else old_experiment.strain[0]
        strain = None if strain_key not in key_to_strain else key_to_strain[strain_key]
        
        #Get reporter
        if old_experiment.reporter is not None:
            from model_new_schema.condition import Reportercondition
            conditions.append(Reportercondition(old_experiment.reporter[1], None, old_experiment.reporter[0]))
        
        #Get allele
        if old_experiment.allele is not None:
            from model_new_schema.condition import Allelecondition
            allele_name = old_experiment.allele[0]
            allele = None if allele_name not in key_to_allele else key_to_allele[allele_name]
            conditions.append(Allelecondition(old_experiment.allele[1], allele))    
            
        #Get chemicals
        from model_new_schema.condition import Chemicalcondition
        for (a, b) in old_experiment.chemicals:
            chemical_key = create_format_name(a)
            chemical = None if chemical_key not in key_to_chemical else key_to_chemical[chemical_key]
            conditions.append(Chemicalcondition(None, chemical, b))
        
        #Get other conditions
        from model_new_schema.condition import Generalcondition
        for (a, b) in old_experiment.condition:
            conditions.append(Generalcondition(a if b is None else a + ': ' + b))
            
        #Get conditions from experiment_comment
        if old_experiment.experiment_comment is not None:
            conditions.append(Generalcondition(old_experiment.experiment_comment))
            
    source_key = old_phenotype_feature.source
    source = None if source_key not in key_to_source else key_to_source[source_key]
        
    new_phenoevidence = NewPhenotypeevidence(source, reference, strain, experiment, note,
                                         bioentity, phenotype, conditions,
                                         old_phenotype_feature.date_created, old_phenotype_feature.created_by)
    return [new_phenoevidence]

def convert_evidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.phenotype import Phenotypeevidence as NewPhenotypeevidence
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.evelement import Experiment as NewExperiment, Strain as NewStrain, Source as NewSource
    from model_new_schema.chemical import Chemical as NewChemical
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.misc import Allele as NewAllele
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    from model_old_schema.reference import Reflink as OldReflink
    from model_old_schema.phenotype import PhenotypeFeature as OldPhenotypeFeature
    
    log = logging.getLogger('convert.phenotype.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source_id',
                       'bioentity_id', 'bioconcept_id']
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        key_to_phenotype = dict([(x.unique_key(), x) for x in new_session.query(NewPhenotype).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(NewStrain).all()])
        key_to_allele = dict([(x.unique_key(), x) for x in new_session.query(NewAllele).all()])
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        key_to_chemical = dict([(x.unique_key(), x) for x in new_session.query(NewChemical).all()])
        
        old_reflinks = old_session.query(OldReflink).all()
        key_to_reflink = dict([((x.col_name, x.primary_key), x) for x in old_reflinks])
        
        already_seen_keys = set()
        
        min_bioent_id = 0
        max_bioent_id = 10000
        num_chunks = ceil(1.0*(max_bioent_id-min_bioent_id)/chunk_size)
        for i in range(0, num_chunks+1):
            min_id = min_bioent_id + i*chunk_size
            max_id = min_bioent_id + (i+1)*chunk_size
            
            #Grab all current objects
            if i < num_chunks:
                current_objs = new_session.query(NewPhenotypeevidence).filter(NewPhenotypeevidence.bioentity_id >= min_id).filter(NewPhenotypeevidence.bioentity_id < max_id).all()
            else:
                current_objs = new_session.query(NewPhenotypeevidence).filter(NewPhenotypeevidence.bioentity_id >= min_id).all()

            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            #Grab old objects
            old_objs = old_session.query(OldPhenotypeFeature).filter(
                                OldPhenotypeFeature.feature_id >= min_id).filter(
                                OldPhenotypeFeature.feature_id < max_id).options(
                                        joinedload('experiment')).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, key_to_reflink, key_to_phenotype, id_to_reference, 
                                                     id_to_bioentity, key_to_strain, key_to_experiment, key_to_allele, key_to_chemical,
                                                     key_to_source)
                    
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        key = newly_created_obj.unique_key()
                        if key not in already_seen_keys:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            
                            if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_id.id)
                            if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_key.id)
                            already_seen_keys.add(key)
                        else:
                            print key
                            
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
    
            #Commit
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
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
    log = set_up_logging('convert.phenotype')
    
    log.info('begin')
        
    convert_phenotype(old_session_maker, new_session_maker)
    
    convert_evidence(old_session_maker, new_session_maker, 1000)
            
    from model_new_schema.phenotype import Phenotypeevidence
    get_bioent_ids_f = lambda x: [x.bioentity_id]
    convert_bioentity_reference(new_session_maker, Phenotypeevidence, 'PHENOTYPE', 'convert.phenotype.bioentity_reference', 10000, get_bioent_ids_f)

    from model_new_schema.phenotype import Phenotype
    convert_disambigs(new_session_maker, Phenotype, ['id', 'format_name'], 'BIOCONCEPT', 'PHENOTYPE', 'convert.phenotype.disambigs', 2000)
    
    log.info('complete')

if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)
    
    
