'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Geninteractionevidence, Physinteractionevidence
from sgdbackend_query import get_evidence, get_evidence_count, get_evidence_snapshot, get_interaction_snapshot
from sgdbackend_query.query_auxiliary import get_interactions, \
    get_interactions_among
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_biocon
from sgdbackend_utils.obj_to_json import minimize_json, evidence_to_json
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
    
def make_details(divided, locus_id=None, reference_id=None):
    from model_new_schema.evidence import Geninteractionevidence, Physinteractionevidence
    genetic_interevidences = get_evidence(Geninteractionevidence, bioent_id=locus_id, reference_id=reference_id)
    physical_interevidences = get_evidence(Physinteractionevidence, bioent_id=locus_id, reference_id=reference_id)

    tables = {}
    if divided:
        tables['genetic'] = {'Error': 'Too much data to display.'} if genetic_interevidences is None else create_simple_table(genetic_interevidences, make_evidence_row, bioent_id=locus_id)
        tables['physical'] = {'Error': 'Too much data to display.'} if physical_interevidences is None else create_simple_table(physical_interevidences, make_evidence_row, bioent_id=locus_id)
        
    else:
        all_interevidences = [x for x in genetic_interevidences]
        all_interevidences.extend(physical_interevidences)
        tables = create_simple_table(all_interevidences, make_evidence_row, bioent_id=locus_id)
        
    return tables  

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
        
    if interevidence.class_type == 'GENINTERACTION':
        phenotype_id = interevidence.phenotype_id
        obj_json = evidence_to_json(interevidence).copy()
        obj_json['bioentity1'] = minimize_json(id_to_bioent[bioent1_id], include_format_name=True)
        obj_json['bioentity2'] = minimize_json(id_to_bioent[bioent2_id], include_format_name=True)
        obj_json['phenotype'] = None if phenotype_id is None else minimize_json(id_to_biocon[phenotype_id])
        obj_json['mutant_type'] = interevidence.mutant_type
        obj_json['interaction_type'] = 'Genetic'
        obj_json['annotation_type'] = interevidence.annotation_type
        obj_json['direction'] = direction
        return obj_json
        
    elif interevidence.class_type == 'PHYSINTERACTION':
        obj_json = evidence_to_json(interevidence).copy()
        obj_json['bioentity1'] = minimize_json(id_to_bioent[bioent1_id], include_format_name=True)
        obj_json['bioentity2'] = minimize_json(id_to_bioent[bioent2_id], include_format_name=True)
        obj_json['modification'] = interevidence.modification
        obj_json['interaction_type'] = 'Physical'
        obj_json['annotation_type'] = interevidence.annotation_type
        obj_json['direction'] = direction
        return obj_json
    else:
        return None

'''
-------------------------------Graph---------------------------------------
'''  

def create_node(bioent, is_focus, gen_ev_count, phys_ev_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'], 
                    'physical': phys_ev_count, 'genetic': gen_ev_count, 'evidence':max(phys_ev_count, gen_ev_count), 
                    'sub_type':sub_type}}

def create_edge(interaction_id, bioent1_id, bioent2_id, total_ev_count, class_type):
    return {'data':{'target': 'Node' + str(bioent1_id), 'source': 'Node' + str(bioent2_id), 
            'evidence':total_ev_count, 'class_type': class_type}}
    
def make_graph(bioent_id):
    neighbor_id_to_genevidence_count = dict([(x.bioentity1_id if x.bioentity2_id==bioent_id else x.bioentity2_id, x.evidence_count) for x in get_interactions('GENINTERACTION', bioent_id)])
    neighbor_id_to_physevidence_count = dict([(x.bioentity1_id if x.bioentity2_id==bioent_id else x.bioentity2_id, x.evidence_count) for x in get_interactions('PHYSINTERACTION', bioent_id)])
    all_neighbor_ids = set()
    all_neighbor_ids.update(neighbor_id_to_genevidence_count.keys())
    all_neighbor_ids.update(neighbor_id_to_physevidence_count.keys())
    
    max_union_count = 0
    max_phys_count = 0
    max_gen_count = 0
    
    evidence_count_to_neighbors = [set() for _ in range(11)]
    evidence_count_to_genetic = [set() for _ in range(11)]
    evidence_count_to_physical = [set() for _ in range(11)]
    
    for neighbor_id in all_neighbor_ids:
        genevidence_count = min(10, 0 if neighbor_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[neighbor_id])
        physevidence_count = min(10, 0 if neighbor_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[neighbor_id])
        gen_and_phys = min(10, max(genevidence_count, physevidence_count))
        
        max_gen_count = max_gen_count if genevidence_count <= max_gen_count else genevidence_count
        max_phys_count = max_phys_count if physevidence_count <= max_phys_count else physevidence_count
        max_union_count = max_union_count if gen_and_phys <= max_union_count else gen_and_phys
        
        evidence_count_to_neighbors[gen_and_phys].add(neighbor_id)
        evidence_count_to_genetic[genevidence_count].add(neighbor_id)
        evidence_count_to_physical[physevidence_count].add(neighbor_id)
        
    #Apply 100 node cutoff
    min_evidence_count = 10
    usable_neighbor_ids = set()
    while len(usable_neighbor_ids) + len(evidence_count_to_neighbors[min_evidence_count]) < 100 and min_evidence_count > 1:
        usable_neighbor_ids.update(evidence_count_to_neighbors[min_evidence_count])
        min_evidence_count = min_evidence_count - 1
      
    tangent_to_genevidence_count = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in get_interactions_among('GENINTERACTION', usable_neighbor_ids, min_evidence_count)])
    tangent_to_physevidence_count = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in get_interactions_among('PHYSINTERACTION', usable_neighbor_ids, min_evidence_count)])
    
    evidence_count_to_phys_tangents = [set() for _ in range(11)]
    evidence_count_to_gen_tangents = [set() for _ in range(11)]
    
    for tangent, evidence_count in tangent_to_genevidence_count.iteritems():
        bioent1_id, bioent2_id = tangent
        if bioent1_id != bioent_id and bioent2_id != bioent_id:
            bioent1_count = max(0 if bioent1_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent1_id],
                            0 if bioent1_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent1_id])
            bioent2_count = max(0 if bioent2_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent2_id],
                            0 if bioent2_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent2_id])
            
            index = min(10, bioent1_count, bioent2_count, evidence_count)
            evidence_count_to_gen_tangents[index].add(tangent)
            
    for tangent, evidence_count in tangent_to_physevidence_count.iteritems():
        bioent1_id, bioent2_id = tangent
        if bioent1_id != bioent_id and bioent2_id != bioent_id:
            bioent1_count = max(0 if bioent1_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent1_id],
                            0 if bioent1_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent1_id])
            bioent2_count = max(0 if bioent2_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent2_id],
                            0 if bioent2_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent2_id])
            
            index = min(10, bioent1_count, bioent2_count, evidence_count)
            evidence_count_to_phys_tangents[index].add(tangent)
        
    #Apply 250 edge cutoff
    old_min_evidence_count = min_evidence_count
    min_evidence_count = 10
    edges = []
    nodes = [create_node(id_to_bioent[bioent_id], True, max_gen_count, max_phys_count)]
    while len(edges) + len(evidence_count_to_physical[min_evidence_count]) + len(evidence_count_to_genetic[min_evidence_count]) + len(evidence_count_to_phys_tangents[min_evidence_count]) + len(evidence_count_to_gen_tangents[min_evidence_count]) < 250 and min_evidence_count > old_min_evidence_count:
        for neighbor_id in evidence_count_to_neighbors[min_evidence_count]:
            physical_count = 0 if neighbor_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[neighbor_id]
            genetic_count = 0 if neighbor_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[neighbor_id]
            nodes.append(create_node(id_to_bioent[neighbor_id], False, genetic_count, physical_count))
        
        for genetic_id in evidence_count_to_genetic[min_evidence_count]:
            genevidence_count = neighbor_id_to_genevidence_count[genetic_id]
            edges.append(create_edge(len(edges), bioent_id, genetic_id, genevidence_count, 'GENETIC'))
                
        for physical_id in evidence_count_to_physical[min_evidence_count]:
            physevidence_count = neighbor_id_to_physevidence_count[physical_id]
            edges.append(create_edge(len(edges), bioent_id, physical_id, physevidence_count, 'PHYSICAL'))
        
        for tangent in evidence_count_to_gen_tangents[min_evidence_count]:
            bioent1_id, bioent2_id = tangent
            gen_ev_count = tangent_to_genevidence_count[tangent]
            edges.append(create_edge(len(edges), bioent1_id, bioent2_id, gen_ev_count, 'GENETIC'))
            
        for tangent in evidence_count_to_phys_tangents[min_evidence_count]:
            bioent1_id, bioent2_id = tangent
            phys_ev_count = tangent_to_physevidence_count[tangent]
            edges.append(create_edge(len(edges), bioent1_id, bioent2_id, phys_ev_count, 'PHYSICAL'))
            
        min_evidence_count = min_evidence_count - 1
    
    return {'nodes': nodes, 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count+1, 'max_evidence_cutoff':max_union_count,
            'max_phys_cutoff': max_phys_count, 'max_gen_cutoff': max_gen_count}

'''
-------------------------------Snapshot---------------------------------------
'''
def make_snapshot():
    snapshot = {}
    snapshot['interaction_type'] = {'Genetic': get_evidence_count(Geninteractionevidence), 'Physical': get_evidence_count(Physinteractionevidence)}

    snapshot['annotation_type'] = get_evidence_snapshot(Geninteractionevidence, 'annotation_type')
    for annot_type, count in get_evidence_snapshot(Physinteractionevidence, 'annotation_type').iteritems():
        if annot_type in snapshot['annotation_type']:
            snapshot['annotation_type'][annot_type] = snapshot['annotation_type'][annot_type] + count
        else:
            snapshot['annotation_type'][annot_type] = count

    snapshot['modification'] = get_evidence_snapshot(Physinteractionevidence, 'modification')
    snapshot['modification']['No Modification'] = snapshot['modification']['No Modification'] + snapshot['interaction_type']['Genetic']

    snapshot['phenotype'] = dict([('No Phenotype' if x is None else id_to_biocon[x]['display_name'], y) for x, y in get_evidence_snapshot(Geninteractionevidence, 'phenotype_id').iteritems()])
    snapshot['phenotype']['No Phenotype'] = snapshot['interaction_type']['Physical'] + snapshot['interaction_type']['Genetic'] - sum(snapshot['phenotype'].values())

    physical_counts1 = get_evidence_snapshot(Physinteractionevidence, 'bioentity1_id')
    physical_counts2 = get_evidence_snapshot(Physinteractionevidence, 'bioentity2_id')
    genetic_counts1 = get_evidence_snapshot(Geninteractionevidence, 'bioentity1_id')
    genetic_counts2 = get_evidence_snapshot(Geninteractionevidence, 'bioentity2_id')

    interaction_counts = get_interaction_snapshot(['PHYSINTERACTION', 'GENINTERACTION'])

    snapshot['annotation_histogram'] = {}
    snapshot['interaction_histogram'] = {}
    for bioent in id_to_bioent.values():
        if bioent['class_type'] == 'LOCUS' and bioent['locus_type'] == 'ORF':
            bioent_id = bioent['id']
            annotation_count = (0 if bioent_id not in physical_counts1 else physical_counts1[bioent_id]) + \
                               (0 if bioent_id not in physical_counts2 else physical_counts2[bioent_id]) + \
                               (0 if bioent_id not in genetic_counts1 else genetic_counts1[bioent_id]) + \
                               (0 if bioent_id not in genetic_counts2 else genetic_counts2[bioent_id])
            interaction_count = 0 if bioent_id not in interaction_counts else interaction_counts[bioent_id]

            if annotation_count not in snapshot['annotation_histogram']:
                snapshot['annotation_histogram'][annotation_count] = 1
            else:
                snapshot['annotation_histogram'][annotation_count] = snapshot['annotation_histogram'][annotation_count] + 1
            if interaction_count not in snapshot['interaction_histogram']:
                snapshot['interaction_histogram'][interaction_count] = 1
            else:
                snapshot['interaction_histogram'][interaction_count] = snapshot['interaction_histogram'][interaction_count] + 1

    for i in range(0, max(snapshot['annotation_histogram'].keys())):
        if i not in snapshot['annotation_histogram']:
            snapshot['annotation_histogram'][i] = 0

    for i in range(0, max(snapshot['interaction_histogram'].keys())):
        if i not in snapshot['interaction_histogram']:
            snapshot['interaction_histogram'][i] = 0
    return snapshot