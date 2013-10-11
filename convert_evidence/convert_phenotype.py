'''
Created on May 6, 2013

@author: kpaskov
'''
from convert_aux.auxillary_tables import convert_bioentity_reference
from convert_utils import set_up_logging, create_or_update, \
    create_format_name, prepare_connections
from convert_utils.link_maker import biocon_link
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
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

def create_phenotype_id(old_phenotype_id):
    return old_phenotype_id + 60000000

def create_phenotype_display_name(observable, qualifier, mutant_type):
    if mutant_type is None:
        mutant_type = 'None'
    if qualifier is None:
        display_name = observable + ' in ' + mutant_type + ' mutant'
    else:
        display_name = qualifier + ' ' + observable + ' in ' + mutant_type + ' mutant'
    return display_name

def create_phenotype_key(observable, qualifier, mutant_type):
    display_name = create_phenotype_display_name(observable, qualifier, mutant_type)
    format_name = create_format_name(display_name)
    return (format_name, 'PHENOTYPE')

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

def create_phenotype(old_phenotype):
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    observable = old_phenotype.observable
    qualifier = old_phenotype.qualifier
    mutant_type = old_phenotype.mutant_type
    
    display_name = create_phenotype_display_name(observable, qualifier, mutant_type)
    format_name = create_format_name(display_name)
    link = biocon_link("Phenotype", format_name)
    new_phenotype = NewPhenotype(create_phenotype_id(old_phenotype.id), display_name, format_name, link,
                                 observable, qualifier, mutant_type, 
                                 create_phenotype_type(old_phenotype.observable),
                                 old_phenotype.date_created, old_phenotype.created_by)
    return [new_phenotype]

def convert_phenotype(old_session_maker, new_session_maker):
    from model_new_schema.phenotype import Phenotype as NewPhenotype
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
        values_to_check = ['phenotype_type', 'display_name', 'description']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        keys_already_seen = set()
            
        #Grab old objects
        old_objs = old_session.query(OldPhenotype).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_phenotype(old_obj)
                
            if newly_created_objs is not None:
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

def create_evidence_id(old_evidence_id):
    return old_evidence_id + 60000000

def create_evidence(old_phenotype_feature, key_to_reflink, key_to_phenotype, 
                         reference_ids, bioent_ids, key_to_strain, key_to_experiment, key_to_allele):
    from model_new_schema.phenotype import Phenotypeevidence as NewPhenotypeevidence
    evidence_id = create_evidence_id(old_phenotype_feature.id)
    reference_id = key_to_reflink[('PHENO_ANNOTATION_NO', old_phenotype_feature.id)].reference_id
    if reference_id not in reference_ids:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    bioent_id = old_phenotype_feature.feature_id
    if bioent_id not in bioent_ids:
        print 'Bioentity does not exist. ' + str(bioent_id)
        return None
    
    phenotype_key = create_phenotype_key(old_phenotype_feature.observable, old_phenotype_feature.qualifier, old_phenotype_feature.mutant_type)
    if phenotype_key not in key_to_phenotype:
        print 'Phenotype does not exist. ' + str(phenotype_key)
        return None
    biocon_id = key_to_phenotype[phenotype_key].id
    
    experiment_key = create_format_name(old_phenotype_feature.experiment_type)
    if experiment_key not in key_to_experiment:
        print 'Experiment does not exist. ' + str(experiment_key)
        return None
    experiment_id = key_to_experiment[experiment_key].id

    strain_id = None
    mutant_allele_id = None
    allele_info = None
    reporter = None 
    reporter_desc = None
    strain_details = None
    experiment_details = None
    conditions = None
    details = None
                                        
    if old_phenotype_feature.experiment is not None:
        experiment = old_phenotype_feature.experiment
        reporter = None if experiment.reporter == None else experiment.reporter[0]
        reporter_desc = None if experiment.reporter == None else experiment.reporter[1]
        strain_key = None if experiment.strain == None else experiment.strain[0]
        strain_details = None if experiment.strain == None else experiment.strain[1]

        strain_id = None
        if strain_key in key_to_strain:
            strain_id = key_to_strain[strain_key].id
        
        allele_info = experiment.allele
        if allele_info is not None:
            allele_name = allele_info[0]
            mutant_allele_id = key_to_allele[allele_name].id
            allele_info = allele_info[1]
    
        comment = experiment.experiment_comment
        if comment is not None:
            experiment_details = comment
            
        if len(experiment.condition) > 0:
            conditions = []
            for (a, b) in experiment.condition:
                if b is None:
                    conditions.append(a)
                else:
                    conditions.append(a + '- ' + b)
            condition_info = ', '.join(conditions)
            conditions = condition_info
            
        if len(experiment.details) > 0:
            details = []
            for (a, b) in experiment.details:
                if b is None:
                    details.append(a)
                else:
                    details.append(a + '- ' + b)
            detail_info = ', '.join(details)
            details = detail_info
        
    new_phenoevidence = NewPhenotypeevidence(evidence_id, experiment_id, reference_id, strain_id,
                                         old_phenotype_feature.source,
                                         bioent_id, biocon_id,
                                         mutant_allele_id, allele_info, 
                                         reporter, reporter_desc, strain_details, experiment_details, conditions, details,
                                         old_phenotype_feature.date_created, old_phenotype_feature.created_by)
    return [new_phenoevidence]

def convert_evidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.phenotype import Phenotypeevidence as NewPhenotypeevidence
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.evelement import Experiment as NewExperiment, Strain as NewStrain
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
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source',
                       'bioentity_id', 'bioconcept_id', 'date_created', 'created_by',
                       'reporter', 'reporter_desc', 'strain_details', 
                       'conditions', 'details', 'experiment_details', 'allele_info', 'allele_id']
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        key_to_phenotype = dict([(x.unique_key(), x) for x in new_session.query(NewPhenotype).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(NewStrain).all()])
        key_to_allele = dict([(x.unique_key(), x) for x in new_session.query(NewAllele).all()])
        bioent_ids = set([x.id for x in new_session.query(NewBioentity).all()])
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
        
        old_reflinks = old_session.query(OldReflink).all()
        key_to_reflink = dict([((x.col_name, x.primary_key), x) for x in old_reflinks])
        
        min_id = old_session.query(func.min(OldPhenotypeFeature.id)).first()[0]
        count = old_session.query(func.max(OldPhenotypeFeature.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewPhenotypeevidence).filter(NewPhenotypeevidence.id >= create_evidence_id(min_id)).filter(NewPhenotypeevidence.id < create_evidence_id(min_id+chunk_size)).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            #Grab old objects
            old_objs = old_session.query(OldPhenotypeFeature).filter(
                                OldPhenotypeFeature.id >= min_id).filter(
                                OldPhenotypeFeature.id < min_id+chunk_size).options(
                                        joinedload('experiment')).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, key_to_reflink, key_to_phenotype, reference_ids, 
                                                     bioent_ids, key_to_strain, key_to_experiment, key_to_allele)
                    
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
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Evidence Chemical ---------------------
"""

def create_evidence_chemical(old_evidence, key_to_chemical, id_to_phenoevidence):
    from model_new_schema.evidence import EvidenceChemical as NewEvidenceChemical
    
    evidence_chemicals = []
        
    new_phenoevidence_id = create_evidence_id(old_evidence.id)
    if new_phenoevidence_id not in id_to_phenoevidence:
        print 'Phenoevidence does not exist. ' + str(new_phenoevidence_id)
        return None
    
    if old_evidence.experiment is not None:
        chemical_infos = old_evidence.experiment.chemicals
        if chemical_infos is not None:   
            for chemical_info in chemical_infos:
                chemical_key = create_format_name(chemical_info[0])
                if chemical_key not in key_to_chemical:
                    print 'Chemical does not exist. ' + chemical_key
                else:
                    chemical_id = key_to_chemical[chemical_key].id
                    chemical_amount = chemical_info[1]
                    evidence_chemicals.append(NewEvidenceChemical(new_phenoevidence_id, chemical_id, chemical_amount, 'PHENOTYPE'))
    return evidence_chemicals

def convert_evidence_chemical(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.phenotype import Phenotypeevidence as NewPhenotypeevidence
    from model_new_schema.chemical import Chemical as NewChemical
    from model_new_schema.evidence import EvidenceChemical as NewEvidenceChemical
    from model_old_schema.phenotype import PhenotypeFeature as OldPhenotypeFeature
    
    log = logging.getLogger('convert.phenotype.evidence_chemical')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['chemical_amt']
        
        #Grab cached dictionaries
        key_to_chemical = dict([(x.unique_key(), x) for x in new_session.query(NewChemical).all()])        

        min_id = old_session.query(func.min(OldPhenotypeFeature.id)).first()[0]
        count = old_session.query(func.max(OldPhenotypeFeature.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewEvidenceChemical).filter(NewEvidenceChemical.evidence_id >= create_evidence_id(min_id)).filter(NewEvidenceChemical.evidence_id < create_evidence_id(min_id+chunk_size)).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            id_to_evidence = dict([(x.id, x) for x in new_session.query(NewPhenotypeevidence).filter(NewPhenotypeevidence.id >= create_evidence_id(min_id)).filter(NewPhenotypeevidence.id < create_evidence_id(min_id+chunk_size)).all()])  
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            #Grab old objects
            old_objs = old_session.query(OldPhenotypeFeature).filter(
                                OldPhenotypeFeature.id >= min_id).filter(
                                OldPhenotypeFeature.id < min_id+chunk_size).options(
                                        joinedload('experiment')).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence_chemical(old_obj, key_to_chemical, id_to_evidence)
                    
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
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
        
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
    
    convert_evidence(old_session_maker, new_session_maker, 10000)
    
    convert_evidence_chemical(old_session_maker, new_session_maker, 10000)
        
    from model_new_schema.phenotype import Phenotypeevidence
    get_bioent_ids_f = lambda x: [x.bioentity_id]
    convert_bioentity_reference(new_session_maker, Phenotypeevidence, 'PHENOTYPE', 'convert.phenotype.bioentity_reference', 10000, get_bioent_ids_f)

    log.info('complete')

if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)
    
    
