'''
Created on May 28, 2013

@author: kpaskov
'''
from schema_conversion import create_or_update_and_remove, cache_by_key, \
    cache_by_id, cache_by_id_in_range, cache_by_key_in_range, cache_ids, \
    cache_ids_in_range

def update_biocon_gene_counts(new_session, biocon_cls, evidence_cls):
    '''
    Update goterm gene counts
    '''

    biocons = new_session.query(biocon_cls).all()
    evidences = new_session.query(evidence_cls).all()
    biocon_id_to_bioent_ids = {}
    
    for biocon in biocons:
        biocon_id_to_bioent_ids[biocon.id] = set()
        
    for evidence in evidences:
        biocon_id_to_bioent_ids[evidence.biocon_id].add(evidence.bioent_id)
        
    num_changed = 0
    for biocon in biocons:
        count = len(biocon_id_to_bioent_ids[biocon.id])
        if count != biocon.direct_gene_count:
            biocon.direct_gene_count = count
            num_changed = num_changed + 1
    print 'In total ' + str(num_changed) + ' changed.'
    return True

def create_interaction_format_name(bioent1, bioent2):
    if bioent1.id < bioent2.id:
        return bioent1.format_name + '__' + bioent2.format_name
    else:
        return bioent2.format_name + '__' + bioent1.format_name

def convert_interactions(new_session, interaction_type, evidence_cls):
    #Cache interactions
    from model_new_schema.interaction import Interaction as NewInteraction
    from model_new_schema.bioentity import Bioentity as NewBioentity
    key_to_interactions = cache_by_key(NewInteraction, new_session, interaction_type=interaction_type)
    key_to_evidence = cache_by_key(evidence_cls, new_session)
    id_to_bioent = cache_by_id(NewBioentity, new_session)
    
    new_interactions = []
    format_name_to_evidence_count = {}
    for evidence in key_to_evidence.values():
        bioent1_id = evidence.bioent1_id
        bioent2_id = evidence.bioent2_id
        bioent1 = id_to_bioent[bioent1_id]
        bioent2 = id_to_bioent[bioent2_id]
        format_name = create_interaction_format_name(bioent1, bioent2)
        if format_name in format_name_to_evidence_count:
            format_name_to_evidence_count[format_name] = format_name_to_evidence_count[format_name] + 1
        else:
            format_name_to_evidence_count[format_name] = 1
        interaction = NewInteraction(evidence.id, format_name, format_name, interaction_type, bioent1_id, bioent2_id, 
                                     bioent1.name_with_link, bioent2.name_with_link)
        new_interactions.append(interaction)
        
    for interaction in new_interactions:
        interaction.evidence_count = format_name_to_evidence_count[interaction.format_name]
        
    values_to_check = ['display_name', 'bioent1_id', 'bioent2_id', 'bioent1_name_with_link', 'bioent2_name_with_link', 'evidence_count']
    success = create_or_update_and_remove(new_interactions, key_to_interactions, values_to_check, new_session)
    return success          
            
def convert_interaction_families(new_session, interaction_types, max_neighbors, min_id, max_id):
    from model_new_schema.interaction import Interaction as NewInteraction, InteractionFamily as NewInteractionFamily
    from model_new_schema.bioentity import Bioentity as NewBioentity
    
    id_to_bioent = cache_by_id(NewBioentity, new_session)
    range_bioent_ids = cache_ids_in_range(NewBioentity, NewBioentity.id, new_session, min_id, max_id)
    key_to_interfams = cache_by_key_in_range(NewInteractionFamily, NewInteractionFamily.bioent_id, new_session, min_id, max_id)
    
    bioent_id_to_neighbors = {}
    for bioent_id in id_to_bioent.keys():
        bioent_id_to_neighbors[bioent_id] = dict()
    
    for interaction_type in interaction_types:
        id_to_interaction = cache_by_id(NewInteraction, new_session, interaction_type=interaction_type)
        for interaction in id_to_interaction.values():
            bioent1_id = interaction.bioent1_id
            bioent2_id = interaction.bioent2_id
            if bioent2_id in bioent_id_to_neighbors[bioent1_id]:
                bioent_id_to_neighbors[bioent1_id][bioent2_id] = bioent_id_to_neighbors[bioent1_id][bioent2_id] + interaction.evidence_count
            else:
                bioent_id_to_neighbors[bioent1_id][bioent2_id] = interaction.evidence_count
            if bioent1_id in bioent_id_to_neighbors[bioent2_id]:
                bioent_id_to_neighbors[bioent2_id][bioent1_id] = bioent_id_to_neighbors[bioent2_id][bioent1_id] + interaction.evidence_count
            else:
                bioent_id_to_neighbors[bioent2_id][bioent1_id] = interaction.evidence_count
           
    interfams = []
                
    for bioent_id in range_bioent_ids:
        neighbors = bioent_id_to_neighbors[bioent_id]
        evidence_cutoffs = [0, 0, 0, 0]
        for evidence_count in neighbors.values():
            index = min(evidence_count, 3)
            evidence_cutoffs[index] = evidence_cutoffs[index]+1
          
        if evidence_cutoffs[2] + evidence_cutoffs[3] > max_neighbors:
            min_evidence_count = 3
        elif evidence_cutoffs[1] + evidence_cutoffs[2] + evidence_cutoffs[3] > max_neighbors:
            min_evidence_count = 2
        else:
            min_evidence_count = 1 
            
        neighbor_ids = set([x for x, y in neighbors.iteritems() if y >= min_evidence_count]) 
            
        for neighbor_id, evidence_count in neighbors.iteritems():
            if evidence_count >= min_evidence_count:
                bioent1_id, bioent2_id = order_bioent_ids(bioent_id, neighbor_id)
                bioent1 = id_to_bioent[bioent1_id]
                bioent2 = id_to_bioent[bioent2_id]
                interfams.append(NewInteractionFamily(bioent_id, bioent1_id, bioent2_id, 
                                                          bioent1.display_name, bioent2.display_name, 
                                                          bioent1.link, bioent2.link, evidence_count))
                
                for neigh_of_neigh_id, evidence_count in bioent_id_to_neighbors[neighbor_id].iteritems():
                    if evidence_count >= min_evidence_count and neigh_of_neigh_id in neighbor_ids:
                        bioent1_id, bioent2_id = order_bioent_ids(neigh_of_neigh_id, neighbor_id)
                        bioent1 = id_to_bioent[bioent1_id]
                        bioent2 = id_to_bioent[bioent2_id]
                        interfams.append(NewInteractionFamily(bioent_id, bioent1_id, bioent2_id, 
                                                          bioent1.display_name, bioent2.display_name, 
                                                          bioent1.link, bioent2.link, evidence_count))
                        
    values_to_check = ['bioent1_display_name', 'bioent2_display_name', 'bioent1_link', 'bioent2_link', 'evidence_count']
    success = create_or_update_and_remove(interfams, key_to_interfams, values_to_check, new_session)
    return success 

def order_bioent_ids(bioent1_id, bioent2_id):
    if bioent1_id < bioent2_id:
        return bioent1_id, bioent2_id
    else:
        return bioent2_id, bioent1_id
    
def convert_gofact(new_session, key_to_evidence, key_to_bioconrels, min_id, max_id):
    from model_new_schema.go import Gofact as NewGofact
    
    key_to_biofacts = cache_by_key_in_range(NewGofact, NewGofact.biocon_id, new_session, min_id, max_id)
    
    child_to_parents = {}
    for bioconrel in key_to_bioconrels.values():
        child_id = bioconrel.child_id
        parent_id = bioconrel.parent_id
        
        if child_id in child_to_parents:
            child_to_parents[child_id].add(parent_id)
        else:
            child_to_parents[child_id] = set([parent_id])
    
    new_biofacts = set()
    for evidence in key_to_evidence.values():
        biocon_ids = [evidence.biocon_id]
        next_gen_biocon_ids = set()
        while len(biocon_ids) > 0:
            for biocon_id in biocon_ids:
                if biocon_id >= min_id and biocon_id < max_id:
                    new_biofacts.add(NewGofact(evidence.bioent_id, biocon_id))
                if biocon_id in child_to_parents:
                    next_gen_biocon_ids.update(child_to_parents[biocon_id])
            biocon_ids = set(next_gen_biocon_ids)
            next_gen_biocon_ids = set()
    success = create_or_update_and_remove(new_biofacts, key_to_biofacts, [], new_session)
    return success

def convert_biocon_ancestors(new_session, bioconrel_type, num_generations):
    from model_new_schema.bioconcept import BioconRelation as NewBioconRelation, BioconAncestor as NewBioconAncestor
    
    #Cache biocon_relations and biocon_ancestors
    key_to_biocon_relations = cache_by_key(NewBioconRelation, new_session, bioconrel_type=bioconrel_type)
    
    child_to_parents = {}
    for biocon_relation in key_to_biocon_relations.values():
        child_id = biocon_relation.child_id
        parent_id = biocon_relation.parent_id
        if child_id not in child_to_parents:
            child_to_parents[child_id] = set()
        if parent_id not in child_to_parents:
            child_to_parents[parent_id] = set()
            
        child_to_parents[child_id].add(parent_id)

    child_to_ancestors = dict([(child_id, [parent_ids]) for child_id, parent_ids in child_to_parents.iteritems()])
    for i in range(2, num_generations):
        for ancestor_ids in child_to_ancestors.values():
            last_generation = ancestor_ids[-1]
            new_generation = set()
            [new_generation.update(child_to_parents[child_id]) for child_id in last_generation]
            ancestor_ids.append(new_generation)
        
    
    for generation in range(1, num_generations):
        print 'Generation ' + str(generation)
        key_to_biocon_ancestors = cache_by_key(NewBioconAncestor, new_session, bioconanc_type=bioconrel_type, generation=generation)
        new_biocon_ancestors = []    

        for child_id, all_ancestor_ids in child_to_ancestors.iteritems():
            this_generation = all_ancestor_ids[generation-1]
            new_biocon_ancestors.extend([NewBioconAncestor(ancestor_id, child_id, bioconrel_type, generation) for ancestor_id in this_generation])
        create_or_update_and_remove(new_biocon_ancestors, key_to_biocon_ancestors, [], new_session) 
    return True
        
