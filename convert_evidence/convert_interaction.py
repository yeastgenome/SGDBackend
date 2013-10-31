'''
Created on May 6, 2013

@author: kpaskov
'''
from convert_other.convert_auxiliary import convert_interaction, convert_bioentity_reference
from convert_utils import create_or_update, set_up_logging, create_format_name, \
    prepare_connections
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_, func
import logging
import sys

'''
 This code is used to convert interaction data from the old schema to the new. It does this by
 creating new schema objects from the old, then comparing these new objects to those already
 stored in the new database. If a newly created object matches one that is already stored, the two
 are compared and the database fields are updated. If a newly created object does not match one that is 
 already stored, it is added to the database.
'''

    
"""
--------------------- Convert Genetic Interaction Evidence ---------------------
"""

def create_interevidence(old_interaction, key_to_experiment, key_to_phenotype,
                         id_to_reference, id_to_bioents, key_to_source, 
                         inter_id_to_feature_ids, inter_id_to_phenotype_key):
    from model_new_schema.evidence import Geninteractionevidence as NewGeninteractionevidence, Physinteractionevidence as NewPhysinteractionevidence
        
    reference_ids = old_interaction.reference_ids
    if len(reference_ids) != 1:
        print 'Too many references'
        return None
    reference_id = reference_ids[0]
    reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
   
    note = old_interaction.interaction_references[0].note
    
    bioent_ids = inter_id_to_feature_ids[old_interaction.id]
    if bioent_ids[0][0] < bioent_ids[1][0]:
        bioent1_id = bioent_ids[0][0]
        bioent2_id = bioent_ids[1][0]
        bait_hit = bioent_ids[0][1] + '-' + bioent_ids[1][1]
    else:
        bioent1_id = bioent_ids[1][0]
        bioent2_id = bioent_ids[0][0]
        bait_hit = bioent_ids[1][1] + '-' + bioent_ids[0][1]
    
    bioentity1 = None if bioent1_id not in id_to_bioents else id_to_bioents[bioent1_id]
    bioentity2 = None if bioent2_id not in id_to_bioents else id_to_bioents[bioent2_id]    
    
    experiment_key = create_format_name(old_interaction.experiment_type)
    experiment = None if experiment_key not in key_to_experiment else key_to_experiment[experiment_key]
    
    source_key = old_interaction.source
    source = None if source_key not in key_to_source else key_to_source[source_key]
    
    if old_interaction.interaction_type == 'genetic interactions':
        phenotype_key = None if old_interaction.id not in inter_id_to_phenotype_key else inter_id_to_phenotype_key[old_interaction.id]
        phenotype = None if phenotype_key is None or phenotype_key not in key_to_phenotype else key_to_phenotype[phenotype_key]
        
        new_genetic_interevidence = NewGeninteractionevidence(source, reference, None, experiment, 
                                                            bioentity1, bioentity2, phenotype, 
                                                            old_interaction.annotation_type, bait_hit, note,
                                                            old_interaction.date_created, old_interaction.created_by)
        return [new_genetic_interevidence]  
    elif old_interaction.interaction_type == 'physical interactions':
        new_physical_interevidence = NewPhysinteractionevidence(source, reference, None, experiment, 
                                                            bioentity1, bioentity2,
                                                            old_interaction.modification, old_interaction.annotation_type, bait_hit, note,
                                                            old_interaction.date_created, old_interaction.created_by)
        return [new_physical_interevidence]      
    return None

def convert_interevidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.evidence import Geninteractionevidence as NewGeninteractionevidence, Physinteractionevidence as NewPhysinteractionevidence
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.evelements import Experiment as NewExperiment, Source as NewSource
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.bioconcept import Phenotype as NewPhenotype, create_phenotype_format_name
    from model_old_schema.interaction import Interaction_Feature as OldInteractionFeature, Interaction_Phenotype as OldInteractionPhenotype, Interaction as OldInteraction
    
    log = logging.getLogger('convert.interaction.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        gen_values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source_id',
                       'bioentity1_id', 'bioentity2_id', 'phenotype_id', 
                       'note', 'annotation_type']
        
        phys_values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source_id',
                       'bioentity1_id', 'bioentity2_id',
                       'modification', 'note', 'annotation_type']
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        key_to_phenotype = dict([(x.unique_key(), x) for x in new_session.query(NewPhenotype).all()])
        id_to_bioent = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
                
        gen_untouched_obj_ids = dict()
        phys_untouched_obj_ids = dict()
        
        used_keys = set()
        
        #Get interaction_features
        inter_id_to_feature_ids = {}
        min_inter_feat_id = old_session.query(func.min(OldInteractionFeature.id)).first()[0]
        max_inter_feat_id = old_session.query(func.max(OldInteractionFeature.id)).first()[0]
        num_inter_feat_chunks = ceil(1.0*(max_inter_feat_id-min_inter_feat_id)/10000)
        for i in range(num_inter_feat_chunks):
            inter_min_id = min_inter_feat_id + i*10000
            inter_max_id = min_inter_feat_id + (i+1)*10000
            for interaction_feature in old_session.query(OldInteractionFeature).filter(OldInteractionFeature.id >= inter_min_id).filter(OldInteractionFeature.id < inter_max_id).all():
                inter_id = interaction_feature.interaction_id
                feature_id = interaction_feature.feature_id
                if inter_id in inter_id_to_feature_ids:
                    inter_id_to_feature_ids[inter_id] = (inter_id_to_feature_ids[inter_id], (feature_id, interaction_feature.action))
                else:
                    inter_id_to_feature_ids[inter_id] = (feature_id, interaction_feature.action)
                    
        #Get interaction_phenotypes
        inter_id_to_phenotype_key = {}
        for phenotype_interaction in old_session.query(OldInteractionPhenotype).options(joinedload('phenotype')).all():
            old_phenotype = phenotype_interaction.phenotype
            phenotype_key = (create_phenotype_format_name(old_phenotype.observable, old_phenotype.qualifier, old_phenotype.mutant_type), 'PHENOTYPE')
            inter_id_to_phenotype_key[phenotype_interaction.interaction_id] = phenotype_key
        
        min_bioent_id = 0
        max_bioent_id = 10000
        num_chunks = ceil(1.0*(max_bioent_id-min_bioent_id)/chunk_size)
        for i in range(0, num_chunks):
            min_id = min_bioent_id + i*chunk_size
            max_id = min_bioent_id + (i+1)*chunk_size
                
            inter_ids = set()
            
            #Grab all current objects
            if i < num_chunks-1:
                gen_current_objs = new_session.query(NewGeninteractionevidence).filter(
                                    or_(NewGeninteractionevidence.bioentity1_id >= min_id)).filter(
                                    or_(NewGeninteractionevidence.bioentity1_id < max_id)).all()
                                        
                phys_current_objs = new_session.query(NewPhysinteractionevidence).filter(
                                    or_(NewPhysinteractionevidence.bioentity1_id >= min_id)).filter(
                                    or_(NewPhysinteractionevidence.bioentity1_id < max_id)).all()
                                        
                for inter_id, feature_ids in inter_id_to_feature_ids.iteritems():
                    feat1, feat2 = feature_ids
                    feat1_id, _ = feat1
                    feat2_id, _ = feat2
                    min_feat_id = min(feat1_id, feat2_id)
                    if min_feat_id >= min_id and min_feat_id < max_id:
                        inter_ids.add(inter_id)
                    
            else:
                gen_current_objs = new_session.query(NewGeninteractionevidence).filter(
                                    or_(NewGeninteractionevidence.bioentity1_id >= min_id)).all()
                                        
                phys_current_objs = new_session.query(NewPhysinteractionevidence).filter(
                                    or_(NewPhysinteractionevidence.bioentity1_id >= min_id)).all() 
                                        
                for inter_id, feature_ids in inter_id_to_feature_ids.iteritems():
                    feat1, feat2 = feature_ids
                    feat1_id, _ = feat1
                    feat2_id, _ = feat2
                    min_feat_id = min(feat1_id, feat2_id)
                    if min_feat_id >= min_id:
                        inter_ids.add(inter_id)
            
            old_objs = set()
            num_id_chunks = ceil(1.0*len(inter_ids)/500)
            inter_id_list = list(inter_ids)
            for j in range(num_id_chunks):
                old_objs.update(old_session.query(OldInteraction).filter(
                                                OldInteraction.id.in_(inter_id_list[500*j: 500*(j+1)])).options(
                                                        joinedload('interaction_references')))
            
            gen_id_to_current_obj = dict([(x.id, x) for x in gen_current_objs])
            gen_key_to_current_obj = dict([(x.unique_key(), x) for x in gen_current_objs])
            gen_untouched_obj_ids.update(gen_id_to_current_obj)
            
            phys_id_to_current_obj = dict([(x.id, x) for x in phys_current_objs])
            phys_key_to_current_obj = dict([(x.unique_key(), x) for x in phys_current_objs])
            phys_untouched_obj_ids.update(phys_id_to_current_obj)

            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_interevidence(old_obj, key_to_experiment, key_to_phenotype, 
                                                          id_to_reference, id_to_bioent, key_to_source,
                                                          inter_id_to_feature_ids, inter_id_to_phenotype_key)
                    
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    class_type = newly_created_obj.class_type
                    
                    if class_type == 'GENINTERACTION':
                        if newly_created_obj.unique_key() not in used_keys:
                            current_obj_by_id = None if newly_created_obj.id not in gen_id_to_current_obj else gen_id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if newly_created_obj.unique_key() not in gen_key_to_current_obj else gen_key_to_current_obj[newly_created_obj.unique_key()]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, gen_values_to_check, new_session, output_creator)
                            
                            if current_obj_by_id is not None and current_obj_by_id.id in gen_untouched_obj_ids:
                                del gen_untouched_obj_ids[current_obj_by_id.id]
                            if current_obj_by_key is not None and current_obj_by_key.id in gen_untouched_obj_ids:
                                del gen_untouched_obj_ids[current_obj_by_key.id]
                            used_keys.add(newly_created_obj.unique_key())
                        else:
                            print newly_created_obj.unique_key()
                    elif class_type == 'PHYSINTERACTION':
                        if newly_created_obj.unique_key() not in used_keys:
                            current_obj_by_id = None if newly_created_obj.id not in phys_id_to_current_obj else phys_id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if newly_created_obj.unique_key() not in phys_key_to_current_obj else phys_key_to_current_obj[newly_created_obj.unique_key()]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, phys_values_to_check, new_session, output_creator)
                            
                            if current_obj_by_id is not None and current_obj_by_id.id in phys_untouched_obj_ids:
                                del phys_untouched_obj_ids[current_obj_by_id.id]
                            if current_obj_by_key is not None and current_obj_by_key.id in phys_untouched_obj_ids:
                                del phys_untouched_obj_ids[current_obj_by_key.id]
                            used_keys.add(newly_created_obj.unique_key())
                        else:
                            print newly_created_obj.unique_key()

            #Commit
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
        
        #Delete untouched objs
        for untouched_obj  in gen_untouched_obj_ids.values():
            new_session.delete(untouched_obj)
            output_creator.removed()
        for untouched_obj  in phys_untouched_obj_ids.values():
            new_session.delete(untouched_obj)
            output_creator.removed()
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
    log = set_up_logging('convert.interaction')
    
    log.info('begin')
        
    convert_interevidence(old_session_maker, new_session_maker, 200)
    
    from model_new_schema.evidence import Physinteractionevidence
    get_bioent_ids_f = lambda x: [x.bioentity1_id, x.bioentity2_id]
    convert_bioentity_reference(new_session_maker, Physinteractionevidence, 'PHYSINTERACTION', 'convert.interaction.physical_bioentity_reference', 10000, get_bioent_ids_f)
    
    from model_new_schema.evidence import Geninteractionevidence
    get_bioent_ids_f = lambda x: [x.bioentity1_id, x.bioentity2_id]
    convert_bioentity_reference(new_session_maker, Geninteractionevidence, 'GENINTERACTION', 'convert.interaction.genetic_bioentity_reference', 10000, get_bioent_ids_f)
          
    convert_interaction(new_session_maker, Physinteractionevidence, 'PHYSINTERACTION', 'convert.physical_interaction.interaction', 10000, False)
    convert_interaction(new_session_maker, Geninteractionevidence, 'GENINTERACTION', 'convert.genetic_interaction.interaction', 10000, False)
 
    log.info('complete')
    
if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)   
   
    
