'''
Created on Mar 15, 2013

@author: kpaskov
'''
from sgdbackend_query import get_evidence
from sgdbackend_query.query_auxiliary import get_interactions
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_reference, \
    id_to_experiment, id_to_strain, id_to_biocon, id_to_source
from sgdbackend_utils.venn import calc_venn_measurements

'''
-------------------------------Overview---------------------------------------
'''  

def make_overview(bioent):
    genetic = get_interactions('GENINTERACTION', bioent['id'])
    physical = get_interactions('PHYSINTERACTION', bioent['id'])
            
    inters_to_genetic = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in genetic])
    inters_to_physical = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in physical])
               
    all_inters = set(inters_to_genetic.keys())
    all_inters.update(inters_to_physical.keys())
    
    A = 0
    B = 0
    C = 0
    for inter in all_inters:
        gen = inter in inters_to_genetic
        phys = inter in inters_to_physical
        if gen:
            A = A+1
        if phys:
            B = B+1
        if gen and phys:
            C = C+1
            
    r, s, x = calc_venn_measurements(A, B, C)
    
    return {'gen_circle_size': r, 'phys_circle_size':s, 'circle_distance': x, 
            'num_gen_interactors': A, 'num_phys_interactors': B, 'num_both_interactors': C}

    
'''
-------------------------------Details---------------------------------------
'''
    
def make_details(divided, bioent_id):
    from model_new_schema.evidence import Geninteractionevidence, Physinteractionevidence
    genetic_interevidences = get_evidence(Geninteractionevidence, bioent_id=bioent_id)
    physical_interevidences = get_evidence(Physinteractionevidence, bioent_id=bioent_id)
            
    tables = {}

    all_interevidences = [x for x in genetic_interevidences]
    all_interevidences.extend(physical_interevidences)

    if divided:
        tables['genetic'] = create_simple_table(genetic_interevidences, make_evidence_row, bioent_id=bioent_id)
        tables['physical'] = create_simple_table(physical_interevidences, make_evidence_row, bioent_id=bioent_id)
        
    else:
        tables = create_simple_table(all_interevidences, make_evidence_row, bioent_id=bioent_id)
        
    return tables  

def minimize_bioent_json(bioent_json):
    if bioent_json is not None:
        return {'display_name': bioent_json['display_name'],
            'format_name': bioent_json['format_name'],
            'link': bioent_json['link']}
    return None
    
def minimize_reference_json(ref_json):
    if ref_json is not None:
        return {'display_name': ref_json['display_name'],
            'link': ref_json['link']}
    return None
    
def minimize_strain_json(strain_json):
    if strain_json is not None:
        return {'display_name': strain_json['display_name'],
            'link': strain_json['link']}
    return None
    
def minimize_experiment_json(exp_json):
    if exp_json is not None:
        return {'display_name': exp_json['display_name'],
            'link': exp_json['link']} 
    return None
    
def minimize_biocon_json(biocon_json):
    if biocon_json is not None:
        return {'display_name': biocon_json['display_name'],
            'link': biocon_json['link']}  
    return None

def make_evidence_row(interevidence, bioent_id=None): 
    if bioent_id is not None:
        if interevidence.bioentity1_id == bioent_id:
            bioent1_id = bioent_id
            bioent2_id = interevidence.bioentity2_id
            direction = interevidence.bait_hit.split('-').pop(1)
        else:
            bioent1_id = bioent_id
            bioent2_id = interevidence.bioentity1_id
            direction = interevidence.bait_hit.split('-').pop(0)
    else:
        bioent1_id = interevidence.bioentity1_id
        bioent2_id = interevidence.bioentity2_id
        direction = interevidence.bait_hit

    reference_id = interevidence.reference_id 
    experiment_id = interevidence.experiment_id
    strain_id = interevidence.strain_id
    note=interevidence.note
    source = id_to_source[interevidence.source_id]
        
    if interevidence.class_type == 'GENINTERACTION':
        phenotype_id = interevidence.phenotype_id
        return {'bioent1': minimize_bioent_json(id_to_bioent[bioent1_id]),
                'bioent2': minimize_bioent_json(id_to_bioent[bioent2_id]),
                'interaction_type': 'Genetic',
                'reference': None if reference_id is None else minimize_reference_json(id_to_reference[reference_id]),
                'experiment': None if experiment_id is None else minimize_experiment_json(id_to_experiment[experiment_id]),
                'strain': None if strain_id is None else minimize_strain_json(id_to_strain[strain_id]),
                'phenotype': None if phenotype_id is None else minimize_biocon_json(id_to_biocon[phenotype_id]),
                'annotation_type': interevidence.annotation_type,
                'direction': direction,
                'source': source,
                'note': note
                }
        
    elif interevidence.class_type == 'PHYSINTERACTION':
        return {'bioent1': minimize_bioent_json(id_to_bioent[bioent1_id]),
                'bioent2': minimize_bioent_json(id_to_bioent[bioent2_id]),
                'interaction_type': 'Physical',
                'reference': None if reference_id is None else minimize_reference_json(id_to_reference[reference_id]),
                'experiment': None if experiment_id is None else minimize_experiment_json(id_to_experiment[experiment_id]),
                'strain': None if strain_id is None else minimize_strain_json(id_to_strain[strain_id]),
                'modification': interevidence.modification,
                'annotation_type': interevidence.annotation_type,
                'direction': direction,
                'source': source,
                'note': note
                }
        
    else:
        return None

'''
-------------------------------Graph---------------------------------------
'''  

def create_interaction_node(bioent_id, bioent_name, bioent_link, is_focus, gen_ev_count, phys_ev_count, total_ev_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent_id), 'name':bioent_name, 'link': bioent_link, 
                    'physical': phys_ev_count, 'genetic': gen_ev_count, 'evidence':total_ev_count, 
                    'sub_type':sub_type}}

def create_interaction_edge(interaction_id, bioent1_id, bioent2_id, gen_ev_count, phys_ev_count, total_ev_count):
    return {'data':{'target': 'Node' + str(bioent1_id), 'source': 'Node' + str(bioent2_id), 
            'physical': phys_ev_count, 'genetic': gen_ev_count, 'evidence':total_ev_count}}
    
def make_graph(bioent_id):
    interaction_families = get_interaction_family(bioent_id)
    
    id_to_node = {}
    edges = []
    min_evidence_count = None
    max_evidence_count = 0
    max_phys_count = 0
    max_gen_count = 0
    max_both_count = 0
    bioent_id_to_evidence_count = {}
    
    for interaction_family in interaction_families:
        evidence_count = interaction_family.evidence_count
        gen_count = interaction_family.genetic_ev_count
        phys_count = interaction_family.physical_ev_count
           
        bioent1_id = interaction_family.bioentity1_id
        bioent2_id = interaction_family.bioentity2_id
        if bioent1_id==bioent_id or bioent2_id==bioent_id:
            if min_evidence_count is None or evidence_count < min_evidence_count:
                min_evidence_count = evidence_count
            if max_evidence_count is None or evidence_count > max_evidence_count:
                max_evidence_count = evidence_count
                
            if max_phys_count is None or phys_count > max_phys_count:
                max_phys_count = phys_count
            if max_gen_count is None or gen_count > max_gen_count:
                max_gen_count = gen_count
            if gen_count > 0 and phys_count > 0 and (max_both_count is None or gen_count + phys_count > max_both_count):
                max_both_count = gen_count + phys_count
            
            if bioent1_id not in bioent_id_to_evidence_count:
                bioent_id_to_evidence_count[bioent1_id] = (gen_count, phys_count, evidence_count)
            else:
                cur_gen_count, cur_phys_count, cur_ev_count = bioent_id_to_evidence_count[bioent1_id]
                if cur_gen_count < gen_count:
                    cur_gen_count = gen_count
                if cur_phys_count < phys_count:
                    cur_phys_count = phys_count
                if cur_ev_count < evidence_count:
                    cur_ev_count = evidence_count
                bioent_id_to_evidence_count[bioent1_id] = (cur_gen_count, cur_phys_count, cur_ev_count)
                
            if bioent2_id not in bioent_id_to_evidence_count:
                bioent_id_to_evidence_count[bioent2_id] = (gen_count, phys_count, evidence_count)
            else:
                cur_gen_count, cur_phys_count, cur_ev_count = bioent_id_to_evidence_count[bioent2_id]
                if cur_gen_count < gen_count:
                    cur_gen_count = gen_count
                if cur_phys_count < phys_count:
                    cur_phys_count = phys_count
                if cur_ev_count < evidence_count:
                    cur_ev_count = evidence_count
                bioent_id_to_evidence_count[bioent2_id] = (cur_gen_count, cur_phys_count, cur_ev_count) 
                            
    for interaction_family in interaction_families:
        bioent1_id = interaction_family.bioentity1_id
        bioent2_id = interaction_family.bioentity2_id
    
        if bioent1_id not in id_to_node:
            bioent1 = id_to_bioent[bioent1_id]
            evidence_counts = bioent_id_to_evidence_count[bioent1_id]
            id_to_node[bioent1_id] = create_interaction_node(bioent1_id, bioent1['display_name'], bioent1['link'], bioent1_id==bioent_id, evidence_counts[0], evidence_counts[1], evidence_counts[2])
        if bioent2_id not in id_to_node:
            bioent2 = id_to_bioent[bioent2_id]
            evidence_counts = bioent_id_to_evidence_count[bioent2_id]
            id_to_node[bioent2_id] = create_interaction_node(bioent2_id, bioent2['display_name'], bioent2['link'], bioent2_id==bioent_id, evidence_counts[0], evidence_counts[1], evidence_counts[2])
        edges.append(create_interaction_edge(interaction_family.id, bioent1_id, bioent2_id, 
                                             interaction_family.genetic_ev_count, interaction_family.physical_ev_count, interaction_family.evidence_count))
            
    
    return {'nodes': id_to_node.values(), 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_count,
            'max_phys_cutoff': max_phys_count, 'max_gen_cutoff': max_gen_count, 'max_both_cutoff': max_both_count}


