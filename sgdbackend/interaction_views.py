'''
Created on Mar 15, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from query import get_resources
from query.query_evidence import get_genetic_interaction_evidence, \
    get_physical_interaction_evidence
from query.query_interaction import get_interactions, get_interaction_family
from sgdbackend.cache import get_cached_bioent, get_cached_experiment, \
    get_cached_reference, get_cached_strain, get_cached_biocon
from sgdbackend.obj_to_json import url_to_json
from sgdbackend.utils import create_simple_table
from sgdbackend.venn import calc_venn_measurements
from sgdbackend.utils import make_reference_list



@view_config(route_name='interaction_overview', renderer='jsonp')
def interaction_overview(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body= entity_type + ' ' + str(identifier) + ' could not be found.')
        
    genetic = get_interactions('GENETIC_INTERACTION', bioent['id'])
    physical = get_interactions('PHYSICAL_INTERACTION', bioent['id'])
    return make_overview(genetic, physical, bioent) 

@view_config(route_name='interaction_details', renderer='jsonp')
def interaction_details(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
        
    genetic_interevidences = get_genetic_interaction_evidence(bioent_id=bioent['id'])
    physical_interevidences = get_physical_interaction_evidence(bioent_id=bioent['id'])
    return make_evidence_tables(False, genetic_interevidences, physical_interevidences, bioent['id']) 
    
@view_config(route_name='interaction_graph', renderer="jsonp")
def interaction_graph(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')  
    return create_interaction_graph(bioent['id'])
    
@view_config(route_name='interaction_resources', renderer="jsonp")
def interaction_resources(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
        
    resources = get_resources('Interactions Resources', bioent_id=bioent['id'])
    resources.sort(key=lambda x: x.display_name)
    return [url_to_json(url) for url in resources]
    
@view_config(route_name='interaction_references', renderer="jsonp")
def interaction_references(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
    return make_reference_list(['GENETIC_INTERACTION_EVIDENCE', 'PHYSICAL_INTERACTION_EVIDENCE'], bioent['id'])


'''
-------------------------------Overview Table---------------------------------------
'''  

def make_overview(genetic, physical, bioent):
    inters_to_genetic = dict([((x.bioent1_id, x.bioent2_id), x.evidence_count) for x in genetic])
    inters_to_physical = dict([((x.bioent1_id, x.bioent2_id), x.evidence_count) for x in physical])
               
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
-------------------------------Evidence Table---------------------------------------
'''
    
def make_evidence_tables(divided, genetic_interevidences, physical_interevidences, bioent_id=None):
    tables = {}

    all_interevidences = [x for x in genetic_interevidences]
    all_interevidences.extend(physical_interevidences)

    if divided:
        tables['genetic'] = create_simple_table(genetic_interevidences, make_evidence_row, bioent_id=bioent_id)
        tables['physical'] = create_simple_table(physical_interevidences, make_evidence_row, bioent_id=bioent_id)
        
    else:
        tables = create_simple_table(all_interevidences, make_evidence_row, bioent_id=bioent_id)
        
    return tables    

def make_evidence_row(interevidence, bioent_id=None): 
    if bioent_id is not None:
        if interevidence.bioent1_id == bioent_id:
            bioent1_id = bioent_id
            bioent2_id = interevidence.bioent2_id
            direction = interevidence.bait_hit.split('-').pop(1)
        else:
            bioent1_id = bioent_id
            bioent2_id = interevidence.bioent1_id
            direction = interevidence.bait_hit.split('-').pop(0)
    else:
        bioent1_id = interevidence.bioent1_id
        bioent2_id = interevidence.bioent2_id
        direction = interevidence.bait_hit

    reference_id = interevidence.reference_id 
    experiment_id = interevidence.experiment_id
    strain_id = interevidence.strain_id
    note=interevidence.note
        
    if interevidence.evidence_type == 'GENETIC_INTERACTION_EVIDENCE':
        return {'bioent1': get_cached_bioent(bioent1_id),
                'bioent2': get_cached_bioent(bioent2_id),
                'interaction_type': 'Genetic',
                'reference': get_cached_reference(reference_id),
                'experiment': get_cached_experiment(experiment_id),
                'strain': get_cached_strain(strain_id),
                'phenotype': get_cached_biocon(interevidence.phenotype_id, 'PHENOTYPE'),
                'annotation_type': interevidence.annotation_type,
                'direction': direction,
                'source': interevidence.source,
                'note': note
                }
        
    elif interevidence.evidence_type == 'PHYSICAL_INTERACTION_EVIDENCE':
        return {'bioent1': get_cached_bioent(bioent1_id),
                'bioent2': get_cached_bioent(bioent2_id),
                'interaction_type': 'Physical',
                'reference': get_cached_reference(reference_id),
                'experiment': get_cached_experiment(experiment_id),
                'strain': get_cached_strain(strain_id),
                'modification': interevidence.modification,
                'annotation_type': interevidence.annotation_type,
                'direction': direction,
                'source': interevidence.source,
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
    
def create_interaction_graph(bioent_id):
    interaction_families = get_interaction_family(bioent_id)
    
    id_to_node = {}
    edges = []
    min_evidence_count = None
    max_evidence_count = None
    max_phys_count = None
    max_gen_count = None
    max_both_count = None
    bioent_id_to_evidence_count = {}
    
    for interaction_family in interaction_families:
        evidence_count = interaction_family.evidence_count
        gen_count = interaction_family.genetic_ev_count
        phys_count = interaction_family.physical_ev_count
           
        bioent1_id = interaction_family.bioent1_id
        bioent2_id = interaction_family.bioent2_id
        if bioent1_id==bioent_id or bioent2_id==bioent_id:
            if min_evidence_count is None or evidence_count < min_evidence_count:
                min_evidence_count = evidence_count
            if max_evidence_count is None or evidence_count > max_evidence_count:
                max_evidence_count = evidence_count
                
            if max_phys_count is None or phys_count > max_phys_count:
                max_phys_count = phys_count
            if max_gen_count is None or gen_count > max_gen_count:
                max_gen_count = gen_count
            if max_both_count is None or min(gen_count, phys_count) > max_both_count:
                max_both_count = min(gen_count, phys_count)
            
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
        bioent1_id = interaction_family.bioent1_id
        bioent2_id = interaction_family.bioent2_id
    
        if bioent1_id not in id_to_node:
            bioent1 = get_cached_bioent(bioent1_id)
            evidence_counts = bioent_id_to_evidence_count[bioent1_id]
            id_to_node[bioent1_id] = create_interaction_node(bioent1_id, bioent1['display_name'], bioent1['link'], bioent1_id==bioent_id, evidence_counts[0], evidence_counts[1], evidence_counts[2])
        if bioent2_id not in id_to_node:
            bioent2 = get_cached_bioent(bioent2_id)
            evidence_counts = bioent_id_to_evidence_count[bioent2_id]
            id_to_node[bioent2_id] = create_interaction_node(bioent2_id, bioent2['display_name'], bioent2['link'], bioent2_id==bioent_id, evidence_counts[0], evidence_counts[1], evidence_counts[2])
        edges.append(create_interaction_edge(interaction_family.id, bioent1_id, bioent2_id, 
                                             interaction_family.genetic_ev_count, interaction_family.physical_ev_count, interaction_family.evidence_count))
            
    
    return {'nodes': id_to_node.values(), 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_count,
            'max_phys_cutoff': max_phys_count, 'max_gen_cutoff': max_gen_count, 'max_both_cutoff': max_both_count}


