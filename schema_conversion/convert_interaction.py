'''
Created on May 6, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, ask_to_commit, \
    prepare_schema_connection, cache_by_key, cache_by_id, create_format_name, \
    cache_by_key_in_range, create_or_update, cache_ids
from schema_conversion.auxillary_tables import update_biorel_evidence_counts
from schema_conversion.convert_phenotype import create_phenotype_key
from sqlalchemy.orm import joinedload
import datetime
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
        format_name = create_interaction_format_name(bioents)
        new_interaction = NewGeneticInteraction(old_interaction.id, format_name, format_name, 
                                          old_interaction.date_created, old_interaction.created_by)
        return new_interaction
    return None

def create_physical_interaction(old_interaction, id_to_bioent):
    from model_new_schema.interaction import PhysicalInteraction as NewPhysicalInteraction
    
    if old_interaction.interaction_type == 'physical interactions':
        bioents = get_bioents_from_feature_ids(old_interaction.feature_ids, id_to_bioent)
        if bioents is None:
            return None
        format_name = create_interaction_format_name(bioents)
        new_interaction = NewPhysicalInteraction(old_interaction.id, format_name, format_name, 
                                          old_interaction.date_created, old_interaction.created_by)
        return new_interaction
    return None

def create_genetic_interaction_bioents(old_interaction, key_to_biorel, id_to_bioent):
    from model_new_schema.bioentity import BioentMultiRelationBioent as NewBioentMultiRelationBioent
    if old_interaction.interaction_type == 'genetic interactions':    
        bioents = get_bioents_from_feature_ids(old_interaction.feature_ids, id_to_bioent)
        if bioents is None:
            return []
        interaction_key = create_interaction_key(bioents, 'GENETIC_INTERACTION')
        
        if interaction_key not in key_to_biorel:
            print 'Interaction does not exist. ' + str(interaction_key)
            return []
        biorel_id = key_to_biorel[interaction_key].id
        
        multirel_bioents = []
        for feat_interact in old_interaction.feature_interactions:
            new_multirel_bioent = NewBioentMultiRelationBioent(biorel_id, feat_interact.feature_id, 'GENETIC_INTERACTION')
            multirel_bioents.append(new_multirel_bioent)
        return multirel_bioents
    return []

def create_physical_interaction_bioents(old_interaction, key_to_biorel, id_to_bioent):
    from model_new_schema.bioentity import BioentMultiRelationBioent as NewBioentMultiRelationBioent
    if old_interaction.interaction_type == 'physical interactions':    
        bioents = get_bioents_from_feature_ids(old_interaction.feature_ids, id_to_bioent)
        if bioents is None:
            return []
        interaction_key = create_interaction_key(bioents, 'PHYSICAL_INTERACTION')
        
        if interaction_key not in key_to_biorel:
            print 'Interaction does not exist. ' + str(interaction_key)
            return []
        biorel_id = key_to_biorel[interaction_key].id
        
        multirel_bioents = []
        for feat_interact in old_interaction.feature_interactions:
            new_multirel_bioent = NewBioentMultiRelationBioent(biorel_id, feat_interact.feature_id, 'PHYSICAL_INTERACTION')
            multirel_bioents.append(new_multirel_bioent)
        return multirel_bioents
    return []

def create_genetic_interevidence(old_interaction, key_to_biorel, id_to_bioent, reference_ids,
                         key_to_phenotype, key_to_experiment):
    from model_new_schema.interaction import GeneticInterevidence as NewGeneticInterevidence
    if old_interaction.interaction_type == 'genetic interactions':
        evidence_id = create_interevidence_id(old_interaction.id)
        reference_ids = old_interaction.reference_ids
        if len(reference_ids) != 1:
            print 'Too many references'
            return None
        reference_id = reference_ids[0]
        if reference_id not in reference_ids:
            print 'Reference does not exist.'
            return None
        
        bioents = get_bioents_from_feature_ids(old_interaction.feature_ids, id_to_bioent)
        if bioents is None:
            return None
        interaction_key = create_interaction_key(bioents, 'GENETIC_INTERACTION')
        
        if interaction_key not in key_to_biorel:
            print 'Interaction does not exist.'
            return None
        biorel_id = key_to_biorel[interaction_key].id
        
        old_phenotypes = old_interaction.interaction_phenotypes
        if len(old_phenotypes) == 0:
            phenotype_id = None
        elif len(old_phenotypes) == 1:
            old_phenotype = old_phenotypes[0].phenotype
            phenotype_key = create_phenotype_key(old_phenotype.observable, old_phenotype.qualifier, old_phenotype.mutant_type)
            
            if phenotype_key not in key_to_phenotype:
                print 'Phenotype does not exist. ' + str(phenotype_key)
                return None
            phenotype_id = key_to_phenotype[phenotype_key].id
        else:
            print 'Too many phenotypes.'
            return None
        
        experiment_key = create_format_name(old_interaction.experiment_type)
        if experiment_key not in key_to_experiment:
            print 'Experiment does not exist. ' + str(experiment_key)
            return None
        experiment_id = key_to_experiment[experiment_key].id
        
        feat_interacts = sorted(old_interaction.feature_interactions, key=lambda x: x.feature_id)
        bait_hit = '-'.join([x.action for x in feat_interacts])
        
        new_genetic_interevidence = NewGeneticInterevidence(evidence_id, biorel_id, experiment_id, reference_id, None, 
                                                        old_interaction.annotation_type, old_interaction.source, 
                                                        phenotype_id, bait_hit,
                                                        old_interaction.date_created, old_interaction.created_by)
        return new_genetic_interevidence  
    return None

def create_physical_interevidence(old_interaction, key_to_biorel, id_to_bioent, reference_ids,
                         key_to_experiment):
    from model_new_schema.interaction import PhysicalInterevidence as NewPhysicalInterevidence
    if old_interaction.interaction_type == 'physical interactions':    
        evidence_id = create_interevidence_id(old_interaction.id)
        reference_ids = old_interaction.reference_ids
        if len(reference_ids) != 1:
            print 'Too many references'
            return None
        reference_id = reference_ids[0]
        
        if reference_id not in reference_ids:
            print 'Reference does not exist.'
            return None
        
        bioents = get_bioents_from_feature_ids(old_interaction.feature_ids, id_to_bioent)
        if bioents is None:
            return None
        interaction_key = create_interaction_key(bioents, 'PHYSICAL_INTERACTION')
        
        if interaction_key not in key_to_biorel:
            print 'Interaction does not exist.'
            return None
        biorel_id = key_to_biorel[interaction_key].id
        
        experiment_key = create_format_name(old_interaction.experiment_type)
        if experiment_key not in key_to_experiment:
            print 'Experiment does not exist. ' + str(experiment_key)
            return None
        experiment_id = key_to_experiment[experiment_key].id
            
        feat_interacts = sorted(old_interaction.feature_interactions, key=lambda x: x.feature_id)
        bait_hit = '-'.join([x.action for x in feat_interacts])
            
        new_genetic_interevidence = NewPhysicalInterevidence(evidence_id, biorel_id, experiment_id, reference_id, None, 
                                                            old_interaction.annotation_type, old_interaction.source, 
                                                            old_interaction.modification, bait_hit,
                                                            old_interaction.date_created, old_interaction.created_by)
        return new_genetic_interevidence  
    return None

  
"""
---------------------Convert------------------------------
"""  

def convert(old_session_maker, new_session_maker, min_id, max_id):

    from model_old_schema.interaction import Interaction as OldInteraction
    
    # Convert genetic_interactions
    print 'Genetic Interaction'
    start_time = datetime.datetime.now()
    new_session = new_session_maker()
    try:
        old_session = old_session_maker()
        old_interactions = old_session.query(OldInteraction).filter(
                                                                    OldInteraction.id >= min_id).filter(
                                                                    OldInteraction.id < max_id).options(
                                                                     joinedload('interaction_references'),
                                                                     joinedload('interaction_phenotypes'),
                                                                     joinedload('feature_interactions')).all()

        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_genetic_interactions(new_session, old_interactions, min_id, max_id)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close() 

    # Convert physic_interactions
    print 'Physical Interaction'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        
        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_physical_interactions(new_session, old_interactions, min_id, max_id)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
    # Convert genetic interaction_bioents
    print 'Genetic Interaction_Bioents'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        
        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_genetic_interaction_bioents(new_session, old_interactions, min_id, max_id)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
    # Convert physical interaction_bioents
    print 'Physical Interaction_Bioents'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        
        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_physical_interaction_bioents(new_session, old_interactions, min_id, max_id)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
    # Convert genetic interevidences
    print 'GeneticInterevidences'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()

        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_genetic_interevidences(new_session, old_interactions, min_id, max_id)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
      
    # Convert physical interevidences
    print 'PhysicalInterevidences'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()

        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_physical_interevidences(new_session, old_interactions, min_id, max_id)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
    # Update evidence_counts for genetic_interactions
    print 'Genetic interaction evidence counts'
    start_time = datetime.datetime.now()
    try:        
        new_session = new_session_maker()
        from model_new_schema.interaction import GeneticInteraction as NewGeneticInteraction, GeneticInterevidence as NewGeneticInterevidence
        success = update_biorel_evidence_counts(new_session, NewGeneticInteraction, NewGeneticInterevidence)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close() 
        
    # Update evidence_counts for physical_interactions
    print 'Physical interaction evidence counts'
    start_time = datetime.datetime.now()
    try:        
        new_session = new_session_maker()
        from model_new_schema.interaction import PhysicalInteraction as NewPhysicalInteraction, PhysicalInterevidence as NewPhysicalInterevidence
        success = update_biorel_evidence_counts(new_session, NewPhysicalInteraction, NewPhysicalInterevidence)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()  
        
        
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

    values_to_check = ['biorel_type', 'display_name', 'date_created', 'created_by']
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
                
def convert_genetic_interaction_bioents(new_session, old_interactions, min_id, max_id):
    '''
    Convert genetic bioentmultirelation_bioents
    '''
    from model_new_schema.interaction import GeneticInteraction as NewGeneticInteraction
    from model_new_schema.bioentity import BioentMultiRelationBioent as NewBioentMultiRelationBioent, Bioentity as NewBioentity

    #Cache bioentmultirelation_bioents
    key_to_bioentmultirelation_bioents = cache_by_key(NewBioentMultiRelationBioent, new_session, biorel_type='GENETIC_INTERACTION')

    key_to_biorel = cache_by_key(NewGeneticInteraction, new_session)
    id_to_bioent = cache_by_id(NewBioentity, new_session)
    
    #Create new bioentmultirelation_bioents if they don't exist, or update the database if they do.
    new_bioentmultirelation_bioents = []
    for old_interaction in old_interactions:
        more = create_genetic_interaction_bioents(old_interaction, key_to_biorel, id_to_bioent)
        new_bioentmultirelation_bioents.extend(more)
    values_to_check = ['biorel_type']
    success = create_or_update(new_bioentmultirelation_bioents, key_to_bioentmultirelation_bioents, values_to_check, new_session)
    return success

def convert_physical_interaction_bioents(new_session, old_interactions, min_id, max_id):
    '''
    Convert physical bioentmultirelation_bioents
    '''
    from model_new_schema.interaction import PhysicalInteraction as NewPhysicalInteraction
    from model_new_schema.bioentity import BioentMultiRelationBioent as NewBioentMultiRelationBioent, Bioentity as NewBioentity

    #Cache bioentmultirelation_bioents
    key_to_bioentmultirelation_bioents = cache_by_key(NewBioentMultiRelationBioent, new_session, biorel_type='PHYSICAL_INTERACTION')

    key_to_biorel = cache_by_key(NewPhysicalInteraction, new_session)
    id_to_bioent = cache_by_id(NewBioentity, new_session)
    
    #Create new bioentmultirelation_bioents if they don't exist, or update the database if they do.
    new_bioentmultirelation_bioents = []
    for old_interaction in old_interactions:
        more = create_physical_interaction_bioents(old_interaction, key_to_biorel, id_to_bioent)
        new_bioentmultirelation_bioents.extend(more)
    values_to_check = ['biorel_type']
    success = create_or_update(new_bioentmultirelation_bioents, key_to_bioentmultirelation_bioents, values_to_check, new_session)
    return success
    
def convert_genetic_interevidences(new_session, old_interactions, min_id, max_id):
    '''
    Convert Genetic Interevidences
    '''
    from model_new_schema.interaction import GeneticInterevidence as NewGeneticInterevidence, GeneticInteraction as NewGeneticInteraction
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.evelement import Experiment as NewExperiment
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    from model_new_schema.reference import Reference as NewReference
    
    #Cache interevidences
    key_to_biorel = cache_by_key(NewGeneticInteraction, new_session)
    key_to_interevidence = cache_by_key_in_range(NewGeneticInterevidence, new_session, min_id, max_id)
    id_to_bioent = cache_by_id(NewBioentity, new_session)
    key_to_experiment = cache_by_key(NewExperiment, new_session)
    key_to_phenotype = cache_by_key(NewPhenotype, new_session)
    reference_ids = cache_ids(NewReference, new_session)

    #Create new genetic interevidences if they don't exist, or update the database if they do.    
    new_genetic_interevidences = [create_genetic_interevidence(x, key_to_biorel, id_to_bioent, reference_ids, key_to_phenotype, key_to_experiment)
                            for x in old_interactions]
   
    values_to_check = ['experiment_id', 'reference_id', 'evidence_type', 'strain_id', 'source',
                       'biorel_id', 'phenotype_id', 'date_created', 'created_by',
                       'annotation_type']
    success = create_or_update_and_remove(new_genetic_interevidences, key_to_interevidence, values_to_check, new_session)
    return success

def convert_physical_interevidences(new_session, old_interactions, min_id, max_id):
    '''
    Convert Physical Interevidences
    '''
    from model_new_schema.interaction import PhysicalInterevidence as NewPhysicalInterevidence, PhysicalInteraction as NewPhysicalInteraction
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.evelement import Experiment as NewExperiment
    from model_new_schema.reference import Reference as NewReference
    
    #Cache interevidences
    key_to_biorel = cache_by_key(NewPhysicalInteraction, new_session)
    key_to_interevidence = cache_by_key_in_range(NewPhysicalInterevidence, new_session, min_id, max_id)
    id_to_bioent = cache_by_id(NewBioentity, new_session)
    key_to_experiment = cache_by_key(NewExperiment, new_session)
    reference_ids = cache_ids(NewReference, new_session)

    #Create new physical interevidences if they don't exist, or update the database if they do.    
    new_physical_interevidences = [create_physical_interevidence(x, key_to_biorel, id_to_bioent, reference_ids, key_to_experiment)
                            for x in old_interactions]
   
    values_to_check = ['experiment_id', 'reference_id', 'evidence_type', 'strain_id', 'source',
                       'biorel_id', 'modification', 'date_created', 'created_by',
                       'annotation_type']
    success = create_or_update_and_remove(new_physical_interevidences, key_to_interevidence, values_to_check, new_session)
    return success
    


if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
#    convert(old_session_maker, new_session_maker, 300000, 400000)
#    convert(old_session_maker, new_session_maker, 400000, 500000)
#    convert(old_session_maker, new_session_maker, 500000, 600000)
#    convert(old_session_maker, new_session_maker, 600000, 700000)
#    convert(old_session_maker, new_session_maker, 700000, 800000)
#    convert(old_session_maker, new_session_maker, 800000, 900000)
#    convert(old_session_maker, new_session_maker, 900000, 1000000)
#    convert(old_session_maker, new_session_maker, 1000000, 1100000)
#    convert(old_session_maker, new_session_maker, 1100000, 1200000)
#    convert(old_session_maker, new_session_maker, 1200000, 1300000)
    convert(old_session_maker, new_session_maker, 1300000, 1400000)
   
    
