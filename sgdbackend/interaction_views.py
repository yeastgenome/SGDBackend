'''
Created on Mar 15, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from query import get_biorels, get_interactions, get_bioent, get_reference_id, \
    get_genetic_interaction_evidence, get_physical_interaction_evidence, \
    get_biorel_id, get_bioent_id, get_resources
from sgdbackend.utils import create_simple_table, make_reference_list



@view_config(route_name='interaction_overview_table', renderer='jsonp')
def interaction_overview_table(request):
    if 'bioent' in request.GET:
        #Need an interaction overview table based on a bioent
        bioent_name = request.GET['bioent']
        bioent = get_bioent(bioent_name, 'LOCUS')
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        genetic = get_biorels('GENETIC_INTERACTION', bioent.id)
        physical = get_biorels('PHYSICAL_INTERACTION', bioent.id)
        return make_overview_tables(genetic, physical, bioent) 
    
    elif 'reference' in request.GET:
        #Need an interaction overview table based on a reference
        ref_name = request.GET['reference']
        ref_id = get_reference_id(ref_name)
        if ref_id is None:
            return Response(status_int=500, body='Reference could not be found.')
        genetic_interevidences = get_genetic_interaction_evidence(reference_id=ref_id)
        physical_interevidences = get_physical_interaction_evidence(reference_id=ref_id)
        genetic = set([interevidence.biorel for interevidence in genetic_interevidences])
        physical = set([interevidence.biorel for interevidence in physical_interevidences])
        return make_overview_tables(genetic, physical) 

    else:
        return Response(status_int=500, body='No Bioent or Reference specified.')


@view_config(route_name='interaction_evidence_table', renderer='jsonp')
def interaction_evidence_table(request):
    if 'biorel' in request.GET:
        #Need an interaction evidence table based on a biorel
        biorel_name = request.GET['biorel']
        biorel_id = get_biorel_id(biorel_name, 'INTERACTION')
        if biorel_id is None:
            return Response(status_int=500, body='Biorel could not be found.')
        genetic_interevidences = get_genetic_interaction_evidence(biorel_id=biorel_id)
        physical_interevidences = get_physical_interaction_evidence(biorel_id=biorel_id)
        return make_evidence_tables(True, genetic_interevidences, physical_interevidences) 
        
    elif 'bioent' in request.GET:
        #Need an interaction evidence table based on a bioent
        bioent_name = request.GET['bioent']
        bioent = get_bioent(bioent_name, 'LOCUS')
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        genetic_interevidences = get_genetic_interaction_evidence(bioent_id=bioent.id)
        physical_interevidences = get_physical_interaction_evidence(bioent_id=bioent.id)
        return make_evidence_tables(True, genetic_interevidences, physical_interevidences, bioent) 
    
    else:
        return Response(status_int=500, body='No Bioent or Biorel specified.')
    
@view_config(route_name='interaction_graph', renderer="jsonp")
def interaction_graph(request):
    if 'bioent' in request.GET:
        #Need an interaction graph based on a bioent
        bioent_name = request.GET['bioent']
        bioent = get_bioent(bioent_name, 'LOCUS')
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        return create_interaction_graph(bioent=bioent)

    else:
        return Response(status_int=500, body='No Bioent specified.')
    
@view_config(route_name='interaction_evidence_resources', renderer='jsonp')
def interaction_evidence_resources(request):
    if 'bioent' in request.GET:
        #Need interaction evidence resources based on a bioent
        bioent_name = request.GET['bioent']
        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
        if bioent_id is None:
            return Response(status_int=500, body='Bioent could not be found.')
        resources = get_resources('Interactions Resources', bioent_id=bioent_id)
        resources.sort(key=lambda x: x.display_name)
        return [url.name_with_link for url in resources]
    
    else:
        return Response(status_int=500, body='No Bioent specified.')
    

'''
-------------------------------Overview Table---------------------------------------
'''

def make_overview_tables(genetic, physical, bioent=None):
    tables = {}
            
    tables['aaData'] = make_overview_table(genetic, physical, bioent)
    return tables    

def make_overview_table(genetic, physical, bioent):
    inters_to_genetic = dict([(x.endpoint_name_with_links, x.evidence_count) for x in genetic])
    inters_to_physical = dict([(x.endpoint_name_with_links, x.evidence_count) for x in physical])
               
    def f(inters, bioent):
        if len(inters) == 1:
            orig_bioent_link = inters[0]
            opp_bioent_link = inters[0]
        else:
            if bioent is not None:
                orig_bioent_link = bioent.name_with_link
            else:
                orig_bioent_link = inters[0]
            opp_bioent_links = list(inters)
            opp_bioent_links.remove(orig_bioent_link)
            opp_bioent_link = opp_bioent_links[0]
            
        if inters in inters_to_genetic:
            genetic_count = inters_to_genetic[inters]
        else:
            genetic_count = 0
        if inters in inters_to_physical:
            physical_count = inters_to_physical[inters]
        else:
            physical_count = 0
        total_count = genetic_count + physical_count
        return [orig_bioent_link, opp_bioent_link, genetic_count, physical_count, total_count]
        
    all_inters = set(inters_to_genetic.keys())
    all_inters.update(inters_to_physical.keys())
    return create_simple_table(all_inters, f, bioent=bioent) 

    
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_evidence_tables(divided, genetic_interevidences, physical_interevidences, bioent=None):
    tables = {}

    all_interevidences = [x for x in genetic_interevidences]
    all_interevidences.extend(physical_interevidences)

    if divided:
        tables['genetic'] = create_simple_table(genetic_interevidences, make_evidence_row, bioent=bioent)
        tables['physical'] = create_simple_table(physical_interevidences, make_evidence_row, bioent=bioent)
        
    else:
        tables['aaData'] = create_simple_table(all_interevidences, make_evidence_row, bioent)
        
    tables['reference'] = make_reference_list(all_interevidences)
        
    return tables    

def make_evidence_row(interevidence, bioent=None): 
    if bioent is not None:
        orig_bioent_link = bioent.name_with_link
        if interevidence.bioent1_id == bioent.id:
            opp_bioent_link = interevidence.bioent2_name_with_link
            direction = interevidence.bait_hit.split('-').pop(1)
        else:
            opp_bioent_link = interevidence.bioent1_name_with_link
            direction = interevidence.bait_hit.split('-').pop(0)
    else:
        orig_bioent_link = interevidence.bioent1_name_with_link
        opp_bioent_link = interevidence.bioent2_name_with_link
        direction = interevidence.bait_hit

    reference_link = interevidence.reference_name_with_link 
    experiment_link = interevidence.experiment_name_with_link
        
    phenotype_link = ''
    if interevidence.evidence_type == 'GENETIC_INTERACTION_EVIDENCE' and interevidence.phenotype_id is not None:
        phenotype_link = interevidence.phenotype_name_with_link
    modification = ''
    if interevidence.evidence_type == 'PHYSICAL_INTERACTION_EVIDENCE' and interevidence.modification is not None:
        modification = interevidence.modification
        
    note=interevidence.note
     
    return [None, orig_bioent_link, opp_bioent_link, 
            experiment_link, interevidence.annotation_type, direction, phenotype_link,
            modification, interevidence.source, reference_link, note]
    
def reverse_direction(direction):
    if direction == 'bait-hit':
        return 'hit-bait'
    else:
        return 'bait-hit'

'''
-------------------------------Graph---------------------------------------
'''  
    
interaction_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
                         {'name':'link', 'type':'string'}, 
                         {'name':'evidence', 'type':'integer'},
                         {'name':'sub_type', 'type':'string'}],
                'edges': [ { 'name': "label", 'type': "string" }, 
                          {'name':'link', 'type':'string'}, 
                          {'name':'evidence', 'type':'integer'}]}

def create_interaction_node(obj, evidence_count, focus_node):
    sub_type = None
    if obj == focus_node:
        sub_type = 'FOCUS'
    return {'id':get_id(obj), 'label':obj.display_name, 'link':obj.link, 'evidence':evidence_count, 'sub_type':sub_type}

def create_interaction_edge(obj, source_obj, sink_obj, evidence_count):
    return { 'id': get_id(obj), 'target': get_id(source_obj), 'source': get_id(sink_obj), 'label': obj.display_name, 'link':obj.link, 
            'evidence':evidence_count}  
    
def weed_out_by_evidence(neighbors, neighbor_evidence_count, max_count=100):
    if len(neighbors) < max_count:
        return neighbors, 1
    
    evidence_to_neighbors = {}
    for neigh in neighbors:
        evidence_count = neighbor_evidence_count[neigh]
        if evidence_count in evidence_to_neighbors:
            evidence_to_neighbors[evidence_count].append(neigh)
        else:
            evidence_to_neighbors[evidence_count] = [neigh]
            
    sorted_keys = sorted(evidence_to_neighbors.keys(), reverse=True)
    keep = []
    min_evidence_count = max(sorted_keys)
    for key in sorted_keys:
        ns = evidence_to_neighbors[key]
        if len(keep) + len(ns) < max_count:
            keep.extend(ns)
            min_evidence_count = key
    return keep, min_evidence_count
    
def create_interaction_graph(bioent):
        
    bioents = set()
    bioent_to_evidence = {}

    #bioents.update([interaction.get_opposite(bioent) for interaction in get_biorels('INTERACTION', bioent)])
    for interaction in get_biorels('PHYSICAL_INTERACTION', bioent.id):
        endpoints = set(interaction.bioentities)
        if len(endpoints) == 2:
            endpoints.remove(bioent)
            opposite = endpoints.pop()
            bioent_to_evidence[opposite] = interaction.evidence_count
    bioents.update(bioent_to_evidence.keys())

    bioents.add(bioent)
    max_evidence_cutoff = 0
    if len(bioent_to_evidence.values()) > 0:
        max_evidence_cutoff = max(bioent_to_evidence.values())
    bioent_to_evidence[bioent] = max_evidence_cutoff
    
    usable_bioents, min_evidence_count = weed_out_by_evidence(bioents, bioent_to_evidence)
    
    nodes = [create_interaction_node(b, bioent_to_evidence[b], bioent) for b in usable_bioents]
    id_to_bioent = dict([(bioent.id, bioent) for bioent in usable_bioents])
    
    node_ids = set([b.id for b in usable_bioents])
    
    interactions = get_interactions(node_ids)

    edges = []
    for interaction in interactions:
        bioent_ids = set([bioent.id for bioent in interaction.bioentities])
        if interaction.evidence_count >= min_evidence_count and len(bioent_ids) == 2 and bioent_ids.issubset(node_ids):
            source_bioent = id_to_bioent[bioent_ids.pop()]
            sink_bioent = id_to_bioent[bioent_ids.pop()]
            edges.append(create_interaction_edge(interaction, source_bioent, sink_bioent, interaction.evidence_count)) 
        
    return {'dataSchema':interaction_schema, 'data': {'nodes': nodes, 'edges': edges}, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_cutoff}

'''
-------------------------------Utils---------------------------------------
'''  
def get_id(bio):
    return bio.type + str(bio.id)

