'''
Created on May 6, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, \
    prepare_schema_connection, cache_by_key, cache_by_id, create_format_name, \
    cache_by_key_in_range, cache_ids, execute_conversion, cache_by_id_in_range, \
    cache_link_by_key, cache_link_by_id, cache_references
from schema_conversion.auxillary_tables import update_biorel_evidence_counts
from schema_conversion.convert_phenotype import create_phenotype_key
from schema_conversion.output_manager import write_to_output_file
from sqlalchemy.orm import joinedload
import model_new_schema
import model_old_schema

'''
 This code is used to convert interaction data from the old schema to the new. It does this by
 creating new schema objects from the old, then comparing these new objects to those already
 stored in the new database. If a newly created object matches one that is already stored, the two
 are compared and the database fields are updated. If a newly created object does not match one that is 
 already stored, it is added to the database.
'''
"""
------------ Create --------------
"""

def create_interevidence_id(old_evidence_id):
    return old_evidence_id

def create_interaction_format_name(bioents):
    bioents.sort(key=lambda x: x.id)
    format_name = '__'.join([bioent.format_name for bioent in bioents])
    return format_name

def create_interaction_key(bioents, biorel_type):
    format_name = create_interaction_format_name(bioents)
    return (format_name, biorel_type)

def get_bioents_from_feature_ids(feature_ids, id_to_bioent):
    bioents = []
    for feature_id in feature_ids:
        if feature_id in id_to_bioent:
            bioents.append(id_to_bioent[feature_id])
        else:
            print 'Bioentity does not exist. ' + feature_id
            return None
    return bioents

def create_genetic_interaction(old_interaction, id_to_bioent):
    from model_new_schema.interaction import GeneticInteraction as NewGeneticInteraction
    
    if old_interaction.interaction_type == 'genetic interactions':
        bioents = get_bioents_from_feature_ids(old_interaction.feature_ids, id_to_bioent)
        if bioents is None:
            return None
        if len(bioents) > 2:
            print 'Too many endpoints.'
            return None
        format_name = create_interaction_format_name(bioents)
        new_interaction = NewGeneticInteraction(old_interaction.id, format_name, format_name, 
                                                bioents[0].id, bioents[1].id,
                                                bioents[0].format_name, bioents[1].format_name,
                                                bioents[0].display_name, bioents[1].display_name,
                                                old_interaction.date_created, old_interaction.created_by)
        return new_interaction
    return None

def create_physical_interaction(old_interaction, id_to_bioent):
    from model_new_schema.interaction import PhysicalInteraction as NewPhysicalInteraction
    
    if old_interaction.interaction_type == 'physical interactions':
        bioents = get_bioents_from_feature_ids(old_interaction.feature_ids, id_to_bioent)
        if bioents is None:
            return None
        if len(bioents) > 2:
            print 'Too many endpoints.'
            return None
        format_name = create_interaction_format_name(bioents)
        new_interaction = NewPhysicalInteraction(old_interaction.id, format_name, format_name, 
                                                 bioents[0].id, bioents[1].id,
                                                 bioents[0].format_name, bioents[1].format_name,
                                                 bioents[0].display_name, bioents[1].display_name,
                                                 old_interaction.date_created, old_interaction.created_by)
        return new_interaction
    return None

def create_genetic_interevidence(old_interaction, experiment_key_to_link, phenotype_key_to_link,
                         reference_id_to_link, bioent_id_to_link):
    from model_new_schema.interaction import GeneticInterevidence as NewGeneticInterevidence
    
    if old_interaction.interaction_type == 'genetic interactions':
        evidence_id = create_interevidence_id(old_interaction.id)
        reference_ids = old_interaction.reference_ids
        if len(reference_ids) != 1:
            print 'Too many references'
            return None
        reference_id = reference_ids[0]
        if reference_id not in reference_id_to_link:
            print 'Reference does not exist.'
            return None
        reference_link, reference_citation = reference_id_to_link[reference_id]
        note = old_interaction.interaction_references[0].note
        
        bioent_ids = list(old_interaction.feature_ids)
        bioent_ids.sort()
        bioent1_id = bioent_ids[0]
        bioent2_id = bioent_ids[1]
        
        if bioent1_id > bioent2_id:
            print 'Out of order.'
            return None
        if bioent1_id not in bioent_id_to_link:
            print 'Bioentity does not exist.'
            return None
        if bioent2_id not in bioent_id_to_link:
            print 'Bioentity does not exist.'
            return None
        bioent1_link = bioent_id_to_link[bioent1_id]
        bioent2_link = bioent_id_to_link[bioent2_id]
        
        old_phenotypes = old_interaction.interaction_phenotypes
        phenotype_id = None
        phenotype_link = None
        if len(old_phenotypes) == 1:
            old_phenotype = old_phenotypes[0].phenotype
            phenotype_key = create_phenotype_key(old_phenotype.observable, old_phenotype.qualifier, old_phenotype.mutant_type)
            
            if phenotype_key not in phenotype_key_to_link:
                print 'Phenotype does not exist. ' + str(phenotype_key)
                return None
            phenotype_id, phenotype_link = phenotype_key_to_link[phenotype_key]
        elif len(old_phenotypes) > 1:
            print 'Too many phenotypes.'
            return None
        
        
        experiment_key = create_format_name(old_interaction.experiment_type)
        if experiment_key not in experiment_key_to_link:
            print 'Experiment does not exist. ' + str(experiment_key)
            return None
        experiment_id, experiment_link = experiment_key_to_link[experiment_key]
        
        feat_interacts = sorted(old_interaction.feature_interactions, key=lambda x: x.feature_id)
        bait_hit = '-'.join([x.action for x in feat_interacts])
        
        new_genetic_interevidence = NewGeneticInterevidence(evidence_id, experiment_id, experiment_link, 
                                                            reference_id, reference_link, reference_citation,
                                                            None, None, 
                                                            old_interaction.annotation_type, old_interaction.source, 
                                                            bioent1_id, bioent2_id, bioent1_link, bioent2_link,
                                                            phenotype_id, phenotype_link,
                                                            bait_hit, note,
                                                            old_interaction.date_created, old_interaction.created_by)
        return new_genetic_interevidence    
    return None

def create_physical_interevidence(old_interaction, experiment_key_to_link,
                         reference_id_to_link, bioent_id_to_link):
    from model_new_schema.interaction import PhysicalInterevidence as NewPhysicalInterevidence
    if old_interaction.interaction_type == 'physical interactions':    
        evidence_id = create_interevidence_id(old_interaction.id)

        reference_ids = old_interaction.reference_ids
        if len(reference_ids) != 1:
            print 'Too many references'
            return None
        reference_id = reference_ids[0]
        note = old_interaction.interaction_references[0].note
        
        if reference_id not in reference_id_to_link:
            print 'Reference does not exist.'
            return None
        reference_link, reference_citation = reference_id_to_link[reference_id]
        
        bioent_ids = list(old_interaction.feature_ids)
        bioent_ids.sort()
        bioent1_id = bioent_ids[0]
        bioent2_id = bioent_ids[1]
        
        if bioent1_id > bioent2_id:
            print 'Out of order.'
            return None
        if bioent1_id not in bioent_id_to_link:
            print 'Bioentity does not exist.'
            return None
        if bioent2_id not in bioent_id_to_link:
            print 'Bioentity does not exist.'
            return None
        bioent1_name_with_link = bioent_id_to_link[bioent1_id]
        bioent2_name_with_link = bioent_id_to_link[bioent2_id]
        
        experiment_key = create_format_name(old_interaction.experiment_type)
        if experiment_key not in experiment_key_to_link:
            print 'Experiment does not exist. ' + str(experiment_key)
            return None
        experiment_id, experiment_link = experiment_key_to_link[experiment_key]
            
        feat_interacts = sorted(old_interaction.feature_interactions, key=lambda x: x.feature_id)
        bait_hit = '-'.join([x.action for x in feat_interacts])
            
        new_genetic_interevidence = NewPhysicalInterevidence(evidence_id, experiment_id, experiment_link,
                                                             reference_id, reference_link, reference_citation,
                                                             None, None,
                                                             old_interaction.annotation_type, old_interaction.source, 
                                                             bioent1_id, bioent2_id, bioent1_name_with_link, bioent2_name_with_link,
                                                             old_interaction.modification, bait_hit, note,
                                                             old_interaction.date_created, old_interaction.created_by)
        return new_genetic_interevidence  
    return None

  
"""
---------------------Convert------------------------------
"""  

def convert(old_session_maker, new_session_maker, ask=True):

    from model_old_schema.interaction import Interaction as OldInteraction
    from model_new_schema.interaction import GeneticInteraction as NewGeneticInteraction, GeneticInterevidence as NewGeneticInterevidence, \
                        PhysicalInteraction as NewPhysicalInteraction, PhysicalInterevidence as NewPhysicalInterevidence
    
    intervals = [300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000, 1400000]
        
#    # Convert genetic_interactions
#    write_to_output_file( 'Genetic Interaction')
#    for i in range(0, len(intervals)-1):
#        min_id = intervals[i]
#        max_id = intervals[i+1]
#        write_to_output_file( 'Interaction ids between ' + str(min_id) + ' and ' + str(max_id))
#        execute_conversion(convert_genetic_interactions, old_session_maker, new_session_maker, ask,
#                       min_id = lambda old_session : min_id,
#                       max_id = lambda old_session : max_id,
#                       old_interactions=lambda old_session: old_session.query(OldInteraction).filter(
#                                                            OldInteraction.id >= min_id).filter(
#                                                            OldInteraction.id < max_id).options(
#                                                            joinedload('feature_interactions')).all())
#
#    # Convert physic_interactions
#    write_to_output_file( 'Physical Interaction')
#    for i in range(0, len(intervals)-1):
#        min_id = intervals[i]
#        max_id = intervals[i+1]
#        write_to_output_file( 'Interaction ids between ' + str(min_id) + ' and ' + str(max_id))
#        execute_conversion(convert_physical_interactions, old_session_maker, new_session_maker, ask,
#                       min_id = lambda old_session : min_id,
#                       max_id = lambda old_session : max_id,
#                       old_interactions=lambda old_session: old_session.query(OldInteraction).filter(
#                                                            OldInteraction.id >= min_id).filter(
#                                                            OldInteraction.id < max_id).options(
#                                                            joinedload('feature_interactions')).all())
    
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.evelement import Experiment as NewExperiment
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    new_session = new_session_maker()
    experiment_key_to_link = cache_link_by_key(NewExperiment, new_session)
    phenotype_key_to_link = cache_link_by_key(NewPhenotype, new_session)
    reference_id_to_link = cache_references(new_session)
    bioent_id_to_link = cache_link_by_id(NewBioentity, new_session)
        
    # Convert genetic interevidences
    write_to_output_file('GeneticInterevidences')
    for i in range(0, len(intervals)-1):
        min_id = intervals[i]
        max_id = intervals[i+1]
        write_to_output_file('Interaction ids between ' + str(min_id) + ' and ' + str(max_id))
        execute_conversion(convert_genetic_interevidences, old_session_maker, new_session_maker, ask,
                       min_id = lambda old_session : min_id,
                       max_id = lambda old_session : max_id,
                       experiment_key_to_link = lambda old_session: experiment_key_to_link,
                       phenotype_key_to_link = lambda old_session: phenotype_key_to_link,
                       reference_id_to_link = lambda old_session: reference_id_to_link,
                       bioent_id_to_link = lambda old_session: bioent_id_to_link,
                       old_interactions=lambda old_session: old_session.query(OldInteraction).filter(
                                                            OldInteraction.id >= min_id).filter(
                                                            OldInteraction.id < max_id).options(
                                                            joinedload('interaction_references'),
                                                            joinedload('interaction_phenotypes'),
                                                            joinedload('feature_interactions')).all())
      
    # Convert physical interevidences
    write_to_output_file( 'PhysicalInterevidences')
    for i in range(0, len(intervals)-1):
        min_id = intervals[i]
        max_id = intervals[i+1]
        write_to_output_file( 'Interaction ids between ' + str(min_id) + ' and ' + str(max_id))
        execute_conversion(convert_physical_interevidences, old_session_maker, new_session_maker, ask,
                       min_id = lambda old_session : min_id,
                       max_id = lambda old_session : max_id,
                       experiment_key_to_link = lambda old_session: experiment_key_to_link,
                       reference_id_to_link = lambda old_session: reference_id_to_link,
                       bioent_id_to_link = lambda old_session: bioent_id_to_link,
                       old_interactions=lambda old_session: old_session.query(OldInteraction).filter(
                                                            OldInteraction.id >= min_id).filter(
                                                            OldInteraction.id < max_id).options(
                                                            joinedload('interaction_references'),
                                                            joinedload('feature_interactions')).all())
        
    # Update evidence_counts for genetic_interactions
    write_to_output_file( 'Genetic interaction evidence counts')
    execute_conversion(update_biorel_evidence_counts, old_session_maker, new_session_maker, ask,
                       biorel_cls = lambda old_session : NewGeneticInteraction,
                       evidence_cls = lambda old_session : NewGeneticInterevidence)
        
    # Update evidence_counts for physical_interactions
    write_to_output_file( 'Physical interaction evidence counts')
    execute_conversion(update_biorel_evidence_counts, old_session_maker, new_session_maker, ask,
                       biorel_cls = lambda old_session : NewPhysicalInteraction,
                       evidence_cls = lambda old_session : NewPhysicalInterevidence)
        
        
def convert_genetic_interactions(new_session, old_interactions, min_id, max_id):
    '''
    Convert Genetic Interactions
    '''
    from model_new_schema.interaction import GeneticInteraction as NewGeneticInteraction
    from model_new_schema.bioentity import Bioentity as NewBioentity
    
    #Cache genetic interactions
    full_mapping = cache_by_key(NewGeneticInteraction, new_session)
    key_to_genetic_interactions = dict([(x, y) for x, y in full_mapping.iteritems() if y.id >= min_id and y.id < max_id])
    id_to_bioent = cache_by_id(NewBioentity, new_session)

    #Create new genetic interactions if they don't exist, or update the database if they do.
    new_genetic_interactions = [create_genetic_interaction(x, id_to_bioent) for x in old_interactions]

    values_to_check = ['biorel_type', 'display_name', 
                       'source_bioent_id', 'sink_bioent_id',
                       'source_format_name', 'sink_format_name',
                       'source_display_name', 'sink_display_name',
                       'date_created', 'created_by']
    success = create_or_update_and_remove(new_genetic_interactions, key_to_genetic_interactions, values_to_check, new_session, full_mapping=full_mapping)
    return success

def convert_physical_interactions(new_session, old_interactions, min_id, max_id):
    '''
    Convert Physical Interactions
    '''
    from model_new_schema.interaction import PhysicalInteraction as NewPhysicalInteraction
    from model_new_schema.bioentity import Bioentity as NewBioentity
    
    #Cache physical interactions
    full_mapping = cache_by_key(NewPhysicalInteraction, new_session)
    key_to_physical_interactions = dict([(x, y) for x, y in full_mapping.iteritems() if y.id >= min_id and y.id < max_id])
    id_to_bioent = cache_by_id(NewBioentity, new_session)

    #Create new physical interactions if they don't exist, or update the database if they do.
    new_physical_interactions = [create_physical_interaction(x, id_to_bioent) for x in old_interactions]

    values_to_check = ['biorel_type', 'display_name', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_physical_interactions, key_to_physical_interactions, values_to_check, new_session, full_mapping=full_mapping)
    return success
                
def convert_genetic_interevidences(new_session, old_interactions=None, experiment_key_to_link=None, phenotype_key_to_link=None,
                                   reference_id_to_link=None, bioent_id_to_link=None, min_id=None, max_id=None):
    '''
    Convert Genetic Interevidences
    '''
    from model_new_schema.interaction import GeneticInterevidence as NewGeneticInterevidence

    
    #Cache interevidences
    key_to_interevidence = cache_by_key_in_range(NewGeneticInterevidence, NewGeneticInterevidence.id, new_session, min_id, max_id)

    #Create new genetic interevidences if they don't exist, or update the database if they do.    
    new_genetic_interevidences = [create_genetic_interevidence(x, experiment_key_to_link, phenotype_key_to_link, reference_id_to_link, bioent_id_to_link)
                            for x in old_interactions]
   
    values_to_check = ['experiment_id', 'experiment_name_with_link',
                       'reference_id', 'reference_name_with_link', 'reference_citation',
                       'evidence_type', 'strain_id', 'strain_name_with_link', 'source',
                       'bioent1_id', 'bioent2_id', 'bioent1_name_with_link', 'bioent2_name_with_link', 
                       'phenotype_id', 'phenotype_name_with_link', 'note',
                       'annotation_type', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_genetic_interevidences, key_to_interevidence, values_to_check, new_session)
    return success

def convert_physical_interevidences(new_session, old_interactions, experiment_key_to_link,
                                   reference_id_to_link, bioent_id_to_link, min_id, max_id):
    '''
    Convert Physical Interevidences
    '''
    from model_new_schema.interaction import PhysicalInterevidence as NewPhysicalInterevidence
    
    #Cache interevidences
    key_to_interevidence = cache_by_key_in_range(NewPhysicalInterevidence, NewPhysicalInterevidence.id, new_session, min_id, max_id)

    #Create new physical interevidences if they don't exist, or update the database if they do.    
    new_physical_interevidences = [create_physical_interevidence(x, experiment_key_to_link, reference_id_to_link, bioent_id_to_link)
                            for x in old_interactions]
   
    values_to_check = ['experiment_id', 'experiment_name_with_link',
                       'reference_id', 'reference_name_with_link', 'reference_citation',
                       'evidence_type', 'strain_id', 'strain_name_with_link', 'source',
                       'bioent1_id', 'bioent2_id', 'bioent1_name_with_link', 'bioent2_name_with_link', 
                       'modification', 'note', 'annotation_type', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_physical_interevidences, key_to_interevidence, values_to_check, new_session)
    return success

if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker, False)
   
    
