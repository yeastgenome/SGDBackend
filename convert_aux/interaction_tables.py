'''
Created on Sep 24, 2013

@author: kpaskov
'''
from convert_utils import create_or_update
from mpmath import ceil
from convert_utils.output_manager import OutputCreator
from sqlalchemy.sql.expression import func, or_
import logging
import sys

"""
--------------------- Convert Interaction ---------------------
"""

def create_interaction_id(evidence_id):
    return evidence_id

def create_directed_key(evidence):
    return create_directed_key_from_bioents(evidence.bioentity1_id, evidence.bioentity2_id)

def create_directed_key_from_bioents(bioent1_id, bioent2_id):
    return (bioent1_id, bioent2_id)    
    
def create_undirected_interaction_format_name(evidence, id_to_bioent):
    bioent1_id = evidence.bioentity1_id
    bioent2_id = evidence.bioentity2_id
    return create_undirected_interaction_format_name_from_bioents(bioent1_id, bioent2_id, id_to_bioent)
    
def create_undirected_interaction_format_name_from_bioents(bioent1_id, bioent2_id, id_to_bioent):
    bioent1 = id_to_bioent[bioent1_id]
    bioent2 = id_to_bioent[bioent2_id]
    
    if bioent1.id < bioent2.id:
        return str(bioent1.format_name + '__' + bioent2.format_name)
    else:
        return str(bioent2.format_name + '__' + bioent1.format_name)

def create_interaction(evidence, evidence_count, id_to_bioent, directed):
    from model_new_schema.auxiliary import Interaction
    bioent1_id = evidence.bioentity1_id
    bioent2_id = evidence.bioentity2_id
    if directed:
        bioent1_id, bioent2_id = create_directed_key(evidence)
        format_name = id_to_bioent[bioent1_id] + '__' + id_to_bioent[bioent2_id]
    else:
        format_name = create_undirected_interaction_format_name(evidence, id_to_bioent)
    interaction = Interaction(create_interaction_id(evidence.id), evidence.class_type, format_name, format_name, bioent1_id, bioent2_id)
    interaction.evidence_count = evidence_count
    return [interaction]

def interaction_precomp(format_name_to_evidence_count, more_evidences, id_to_bioent, directed):
    for evidence in more_evidences:
        if directed:
            format_name = create_directed_key(evidence)
        else:
            format_name = create_undirected_interaction_format_name(evidence, id_to_bioent)
            
        
        if format_name in format_name_to_evidence_count:
            format_name_to_evidence_count[format_name] = format_name_to_evidence_count[format_name] + 1
        else:
            format_name_to_evidence_count[format_name] = 1

def convert_interaction(new_session_maker, evidence_class, class_type,  label, chunk_size, directed):
    from model_new_schema.auxiliary import Interaction
    from model_new_schema.bioentity import Bioentity
    
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['display_name', 'bioentity1_id', 'bioentity2_id', 'evidence_count']   
        
        #Grab all current objects
        current_objs = new_session.query(Interaction).filter(Interaction.class_type == class_type).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        #Grab cached dictionaries
        id_to_bioent = dict([(x.id, x) for x in new_session.query(Bioentity).all()])
            
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        used_unique_keys = set()   
        
        #Precomp evidence count
        format_name_to_evidence_count = {}
        min_id = new_session.query(func.min(evidence_class.id)).first()[0]
        count = new_session.query(func.max(evidence_class.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):  
            more_old_objs = new_session.query(evidence_class).filter(evidence_class.id >= min_id).filter(evidence_class.id < min_id+chunk_size).all()
            interaction_precomp(format_name_to_evidence_count, more_old_objs, id_to_bioent, directed)
            min_id = min_id + chunk_size

        #Create interactions
        min_id = new_session.query(func.min(evidence_class.id)).first()[0]
        count = new_session.query(func.max(evidence_class.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):  
            old_objs = new_session.query(evidence_class).filter(evidence_class.id >= min_id).filter(evidence_class.id < min_id+chunk_size).all()    
            for old_obj in old_objs:
                #Convert old objects into new ones
                if directed:
                    format_name = create_directed_key(old_obj)
                else:
                    format_name = create_undirected_interaction_format_name(old_obj, id_to_bioent)
                evidence_count = format_name_to_evidence_count[format_name]
                newly_created_objs = create_interaction(old_obj, evidence_count, id_to_bioent, directed)
         
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        if unique_key not in used_unique_keys:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            used_unique_keys.add(unique_key)
                            
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                            
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
            
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
        
    log.info('complete')
    

    
"""
--------------------- Convert Regulation Family---------------------
"""

def create_regulation_family(bioentity, evidence_cutoff, bioent_id_to_target_ids, bioent_id_to_regulator_ids, edge_to_counts, id_to_bioent):
    from model_new_schema.auxiliary import RegulationFamily
    
    regulation_families = {}
    evidence_count_to_regulation_family_key = [None, set(), set(), set(), set(), set(), set(), set(), set(), set(), set()]
    neighbor_id_to_evidence_count = {}
    
    #Create start graph
    bioentity_id = bioentity.id
    
    included_neighbor_ids = set()
    
    #Add targets
    target_ids = bioent_id_to_target_ids[bioentity_id]
    for target_id in target_ids:
        key = create_directed_key_from_bioents(bioentity_id, target_id)
        if key not in regulation_families:
            total_count = edge_to_counts[key]
            
            if total_count >= evidence_cutoff:
                regulation_families[key] = RegulationFamily(bioentity_id, bioentity_id, target_id, total_count)
                evidence_count_to_regulation_family_key[min(total_count, 10)].add(key)
                included_neighbor_ids.add(target_id)
                neighbor_id_to_evidence_count[target_id] = total_count
                
    #Add regulators           
    regulator_ids = bioent_id_to_regulator_ids[bioentity_id]
    for regulator_id in regulator_ids:
        key = create_directed_key_from_bioents(regulator_id, bioentity_id)
        if key not in regulation_families:
            total_count = edge_to_counts[key]
             
            if total_count >= evidence_cutoff:
                regulation_families[key] = RegulationFamily(bioentity_id, regulator_id, bioentity_id, total_count)
                evidence_count_to_regulation_family_key[min(total_count, 10)].add(key)
                included_neighbor_ids.add(regulator_id)
                neighbor_id_to_evidence_count[regulator_id] = total_count
                 
    #Create connections across star.
    for neighbor_id in included_neighbor_ids:
        target_of_neigh_ids = bioent_id_to_target_ids[neighbor_id] & included_neighbor_ids
        for overlap_id in target_of_neigh_ids:
            key = create_directed_key_from_bioents(neighbor_id, overlap_id)
            if key not in regulation_families:
                total_count = edge_to_counts[key]
             
                if total_count >= evidence_cutoff:
                    regulation_families[key] = RegulationFamily(bioentity_id, neighbor_id, overlap_id, total_count)
                    edge_appear_ev_count = min([total_count, neighbor_id_to_evidence_count[neighbor_id], neighbor_id_to_evidence_count[overlap_id], 10])
                    evidence_count_to_regulation_family_key[edge_appear_ev_count].add(key)
                    
        regulator_of_neigh_ids = bioent_id_to_regulator_ids[neighbor_id] & included_neighbor_ids
        for overlap_id in regulator_of_neigh_ids:
            key = create_directed_key_from_bioents(overlap_id, neighbor_id)
            if key not in regulation_families:
                total_count = edge_to_counts[key]
             
                if total_count >= evidence_cutoff:
                    regulation_families[key] = RegulationFamily(bioentity_id, overlap_id, neighbor_id, total_count)
                    edge_appear_ev_count = min([total_count, neighbor_id_to_evidence_count[neighbor_id], neighbor_id_to_evidence_count[overlap_id], 10])
                    evidence_count_to_regulation_family_key[edge_appear_ev_count].add(key)
                    
    reg_fams = []
    i = 10
    while i > 0 and len(reg_fams) + len(evidence_count_to_regulation_family_key[i]) < 250:
        reg_fams.extend([regulation_families[x] for x in evidence_count_to_regulation_family_key[i]])
        i = i - 1
           
    return reg_fams

def regulation_family_precomp(regulations, max_neighbors, id_to_bioent):
    bioent_id_to_target_ids = {}
    bioent_id_to_regulator_ids = {}
    edge_to_counts = {}
    
    # Build a set of neighbors for every bioent.
    for bioent_id in id_to_bioent.keys():
        bioent_id_to_target_ids[bioent_id] = set()
        bioent_id_to_regulator_ids[bioent_id] = set()
        
    for regulation in regulations:
        bioent1_id = regulation.bioentity1_id
        bioent2_id = regulation.bioentity2_id
        bioent_id_to_target_ids[bioent1_id].add(bioent2_id)
        bioent_id_to_regulator_ids[bioent2_id].add(bioent1_id)
                
    # Build a set of maximum counts for each edge
    for regulation in regulations:
        key = create_directed_key(regulation)
        edge_to_counts[key]  = regulation.evidence_count
                      
    bioent_id_to_evidence_cutoff = {}
              
    for bioent_id in id_to_bioent.keys():
        target_ids = bioent_id_to_target_ids[bioent_id]
        regulator_ids = bioent_id_to_regulator_ids[bioent_id]
        
        # Calculate evidence cutoffs.
        evidence_cutoffs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for target_id in target_ids:
            key = create_directed_key_from_bioents(bioent_id, target_id)
            neigh_ev_count = edge_to_counts[key]
            index = min(neigh_ev_count, 10)
            evidence_cutoffs[index] = evidence_cutoffs[index]+1
            
        for regulator_id in regulator_ids:
            key = create_directed_key_from_bioents(regulator_id, bioent_id)
            neigh_ev_count = edge_to_counts[key]
            index = min(neigh_ev_count, 10)
            evidence_cutoffs[index] = evidence_cutoffs[index]+1
         
        total = evidence_cutoffs[10]
        i = 9
        min_evidence_count = None
        while i >= 1 and min_evidence_count is None:
            if evidence_cutoffs[i] + total > max_neighbors:
                min_evidence_count = i+1
            else:
                total = evidence_cutoffs[i] + total
                i = i-1
        if min_evidence_count is None:
            min_evidence_count = 1
            
        bioent_id_to_evidence_cutoff[bioent_id] = min_evidence_count
        
    return bioent_id_to_evidence_cutoff, bioent_id_to_target_ids, bioent_id_to_regulator_ids, edge_to_counts

def convert_regulation_family(new_session_maker, chunk_size):
    from model_new_schema.auxiliary import Interaction, RegulationFamily
    from model_new_schema.bioentity import Bioentity
    
    log = logging.getLogger('convert.regulation.regulation_family')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['evidence_count']   
        
        #Grab cached dictionaries
        id_to_bioent = dict([(x.id, x) for x in new_session.query(Bioentity).all()]) 
        
        #Grab old objs
        regulations = new_session.query(Interaction).filter(Interaction.class_type == 'REGULATION').all()
        
        bioent_id_to_evidence_cutoff, bioent_id_to_target_ids, bioent_id_to_regulator_ids, edge_to_counts = regulation_family_precomp(regulations, 100, id_to_bioent)
        
        min_id = 0
        count = new_session.query(func.max(Bioentity.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks): 
            #Grab all current objects
            current_objs = new_session.query(RegulationFamily).filter(RegulationFamily.bioentity_id >= min_id).filter(RegulationFamily.bioentity_id < min_id + chunk_size).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
             
            old_objs = new_session.query(Bioentity).filter(Bioentity.id >= min_id).filter(Bioentity.id < min_id+chunk_size).all()  
            for old_obj in old_objs:
                #Convert old objects into new ones
                evidence_cutoff = bioent_id_to_evidence_cutoff[old_obj.id]
                newly_created_objs = create_regulation_family(old_obj, evidence_cutoff, 
                                bioent_id_to_target_ids, bioent_id_to_regulator_ids, edge_to_counts, id_to_bioent)
         
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
            
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                            
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
                
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Interaction Family---------------------
"""

def create_interaction_family(bioentity, evidence_cutoff, bioent_id_to_neighbor_ids, edge_to_counts, id_to_bioent):
    from model_new_schema.auxiliary import InteractionFamily as NewInteractionFamily
    
    interaction_families = {}
    evidence_count_to_interaction_family_key = [None, set(), set(), set(), set(), set(), set(), set(), set(), set(), set()]
    neighbor_id_to_evidence_count = {}
    
    #Create start graph
    bioentity_id = bioentity.id
    neighbor_ids = bioent_id_to_neighbor_ids[bioentity_id]
    included_neighbor_ids = set()
    for neighbor_id in neighbor_ids:
        key = create_undirected_interaction_format_name_from_bioents(bioentity_id, neighbor_id, id_to_bioent)
        if key not in interaction_families:
            edge_counts = edge_to_counts[key]
            phys_count = 0 if 'PHYSINTERACTION' not in edge_counts else edge_counts['PHYSINTERACTION']
            gen_count = 0 if 'GENINTERACTION' not in edge_counts else edge_counts['GENINTERACTION']
            total_count = sum(edge_counts.values())
            
            if total_count >= evidence_cutoff:
                interaction_families[key] = NewInteractionFamily(bioentity_id, bioentity_id, neighbor_id, gen_count, phys_count, total_count)
                included_neighbor_ids.add(neighbor_id)
                evidence_count_to_interaction_family_key[min(total_count, 10)].add(key)
                neighbor_id_to_evidence_count[neighbor_id] = total_count
                
    #Create connections across star.
    for neighbor_id in neighbor_ids:
        if neighbor_id in included_neighbor_ids:
            neigh_of_neigh_ids = bioent_id_to_neighbor_ids[neighbor_id] & included_neighbor_ids
            overlap = neigh_of_neigh_ids & neighbor_ids
            for overlap_id in overlap:
                key = create_undirected_interaction_format_name_from_bioents(overlap_id, neighbor_id, id_to_bioent)
                if key not in interaction_families:
                    edge_counts = edge_to_counts[key]
                    phys_count = 0 if 'PHYSINTERACTION' not in edge_counts else edge_counts['PHYSINTERACTION']
                    gen_count = 0 if 'GENINTERACTION' not in edge_counts else edge_counts['GENINTERACTION']
                    total_count = sum(edge_counts.values())
                
                    if total_count >= evidence_cutoff:
                        interaction_families[key] = NewInteractionFamily(bioentity_id, overlap_id, neighbor_id, gen_count, phys_count, total_count)
                        edge_appear_ev_count = min([total_count, neighbor_id_to_evidence_count[neighbor_id], neighbor_id_to_evidence_count[overlap_id], 10])
                        evidence_count_to_interaction_family_key[edge_appear_ev_count].add(key)
                
    inter_fams = []
    i = 10
    while i > 0 and len(inter_fams) + len(evidence_count_to_interaction_family_key[i]) < 250:
        inter_fams.extend([interaction_families[x] for x in evidence_count_to_interaction_family_key[i]])
        i = i - 1
           
    return inter_fams

def interaction_family_precomp(interactions, max_neighbors, id_to_bioent):
    bioent_id_to_neighbor_ids = {}
    edge_to_counts = {}
    
    # Build a set of neighbors for every bioent.
    for bioent_id in id_to_bioent.keys():
        bioent_id_to_neighbor_ids[bioent_id] = set()
        
    for interaction in interactions:
        bioent1_id = interaction.bioentity1_id
        bioent2_id = interaction.bioentity2_id
        if bioent2_id not in bioent_id_to_neighbor_ids[bioent1_id]:
            bioent_id_to_neighbor_ids[bioent1_id].add(bioent2_id)
        if bioent1_id not in bioent_id_to_neighbor_ids[bioent2_id]:
            bioent_id_to_neighbor_ids[bioent2_id].add(bioent1_id)
                
    # Build a set of maximum counts for each interaction_type for each edge
    for interaction in interactions:
        interaction_type = interaction.class_type
        key = create_undirected_interaction_format_name(interaction, id_to_bioent)
            
        if key not in edge_to_counts:
            edge_to_counts[key]  = {interaction_type: interaction.evidence_count}
        elif interaction_type in edge_to_counts[key]:
            edge_to_counts[key][interaction_type] = edge_to_counts[key][interaction_type] + interaction.evidence_count
        else:
            edge_to_counts[key][interaction_type] = interaction.evidence_count
                      
    bioent_id_to_evidence_cutoff = {}
          
    for bioent_id in id_to_bioent.keys():
        neighbor_ids = bioent_id_to_neighbor_ids[bioent_id]
        
        # Calculate evidence cutoffs.
        evidence_cutoffs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for neighbor_id in neighbor_ids:
            key = create_undirected_interaction_format_name_from_bioents(bioent_id, neighbor_id, id_to_bioent)
            neigh_ev_count = sum(edge_to_counts[key].values())
            index = min(neigh_ev_count, 10)
            evidence_cutoffs[index] = evidence_cutoffs[index]+1
         
        total = evidence_cutoffs[10]
        i = 9
        min_evidence_count = None
        while i >= 1 and min_evidence_count is None:
            if evidence_cutoffs[i] + total > max_neighbors:
                min_evidence_count = i+1
            else:
                total = evidence_cutoffs[i] + total
                i = i-1
        if min_evidence_count is None:
            min_evidence_count = 1
            
        bioent_id_to_evidence_cutoff[bioent_id] = min_evidence_count
        
        
        # Calculate evidence cutoffs.
        evidence_cutoffs = [0, 0, 0, 0]
        for neighbor_id in neighbor_ids:
            key = create_undirected_interaction_format_name_from_bioents(bioent_id, neighbor_id, id_to_bioent)
            neigh_ev_count = sum(edge_to_counts[key].values())
            index = min(neigh_ev_count, 3)
            evidence_cutoffs[index] = evidence_cutoffs[index]+1
          
        if evidence_cutoffs[2] + evidence_cutoffs[3] > max_neighbors:
            min_evidence_count = 3
        elif evidence_cutoffs[1] + evidence_cutoffs[2] + evidence_cutoffs[3] > max_neighbors:
            min_evidence_count = 2
        else:
            min_evidence_count = 1 
            
        bioent_id_to_evidence_cutoff[bioent_id] = min_evidence_count
        
    return bioent_id_to_evidence_cutoff, bioent_id_to_neighbor_ids, edge_to_counts

def convert_interaction_family(new_session_maker, chunk_size):
    from model_new_schema.auxiliary import Interaction, InteractionFamily
    from model_new_schema.bioentity import Bioentity
    
    log = logging.getLogger('convert.interaction.interaction_family')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['bioentity1_id', 'bioentity2_id', 'genetic_ev_count', 'physical_ev_count', 'evidence_count']   
        
        #Grab cached dictionaries
        id_to_bioent = dict([(x.id, x) for x in new_session.query(Bioentity).all()]) 
        
        #Grab old objs
        interactions = new_session.query(Interaction).filter(or_(Interaction.class_type == 'PHYSINTERACTION', Interaction.class_type == 'GENINTERACTION')).all()
        
        bioent_id_to_evidence_cutoff, bioent_id_to_neighbor_ids, edge_to_counts = interaction_family_precomp(interactions, 100, id_to_bioent)
        
        min_id = 0
        count = new_session.query(func.max(Bioentity.id)).first()[0]
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks): 
            #Grab all current objects
            current_objs = new_session.query(InteractionFamily).filter(InteractionFamily.bioentity_id >= min_id).filter(InteractionFamily.bioentity_id < min_id + chunk_size).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
             
            old_objs = new_session.query(Bioentity).filter(Bioentity.id >= min_id).filter(Bioentity.id < min_id+chunk_size).all()  
            for old_obj in old_objs:
                #Convert old objects into new ones
                evidence_cutoff = bioent_id_to_evidence_cutoff[old_obj.id]
                newly_created_objs = create_interaction_family(old_obj, evidence_cutoff, 
                                    bioent_id_to_neighbor_ids, edge_to_counts, id_to_bioent)
         
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
            
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                            
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
                
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        
    log.info('complete')