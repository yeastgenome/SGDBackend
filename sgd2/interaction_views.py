'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import LinkMaker
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent, get_biorels, get_biorel, get_interaction_evidence, \
    get_interactions, get_reference, get_interaction_evidence_ref
from sgd2.views import site_layout
from utils.utils import create_simple_table, \
    make_reference_list, entry_with_link


'''
-------------------------------Views---------------------------------------
'''
@view_config(route_name='interaction_evidence', renderer='templates/interaction_evidence.pt')
def interaction_evidence(request):
    if 'biorel_name' in request.GET:
        #Need an interaction evidence page based on a biorel
        biorel_name = request.GET['biorel_name']
        biorel = get_biorel(biorel_name, 'INTERACTION')
        if biorel is None:
            return Response(status_int=500, body='Biorel could not be found.')
        name = biorel.name
        description = 'Interaction between ' + biorel.source_bioent.name + ' and ' + biorel.sink_bioent.name
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'description':description, 'hide_interactor':True,
                'bioent1':biorel.source_bioent, 'bioent2':biorel.sink_bioent, 'link_maker':LinkMaker(biorel.name, biorel=biorel)}
        
    elif 'bioent_name' in request.GET:
        #Need an interaction evidence page based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        name = 'Interaction Evidence for ' + bioent.name
        description = 'Evidence for all interactions associated with ' + bioent.name
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'description':description, 'hide_interactor':False,
                'bioent1':bioent, 'bioent2':None, 'link_maker':LinkMaker(bioent.name, bioent=bioent)}

    else:
        return Response(status_int=500, body='No Bioent or Biorel specified.')

@view_config(route_name='interaction_overview_table', renderer='json')
def interaction_overview_table(request):
    if 'bioent_name' in request.GET:
        #Need an interaction overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        biorels = get_biorels('INTERACTION', bioent)
        #interevidences = get_interaction_evidence(biorels)
        return make_overview_tables(False, biorels, bioent) 
    
    elif 'reference_name' in request.GET:
        #Need an interaction overview table based on a reference
        ref_name = request.GET['reference_name']
        ref = get_reference(ref_name)
        if ref is None:
            return Response(status_int=500, body='Reference could not be found.')
        interevidences = get_interaction_evidence_ref(ref)
        biorels = set([interevidence.biorel for interevidence in biorels])
        return make_overview_tables(False, interevidences) 

    else:
        return Response(status_int=500, body='No Bioent or Reference specified.')


@view_config(route_name='interaction_evidence_table', renderer='json')
def interaction_evidence_table(request):
    if 'biorel_name' in request.GET:
        #Need an interaction overview table based on a biorel
        biorel_name = request.GET['biorel_name']
        biorel = get_biorel(biorel_name, 'INTERACTION')
        if biorel is None:
            return Response(status_int=500, body='Biorel could not be found.')
        return make_evidence_tables(True, [biorel]) 
        
    elif 'bioent_name' in request.GET:
        #Need an interaction overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        biorels = get_biorels('INTERACTION', bioent=bioent)
        return make_evidence_tables(True, biorels, bioent) 
    
    else:
        return Response(status_int=500, body='No Bioent or Biorel specified.')
    
@view_config(route_name='interaction_graph', renderer="json")
def interaction_graph(request):
    if 'bioent_name' in request.GET:
        #Need an interaction graph based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        return create_interaction_graph(bioent=bioent)

    else:
        return Response(status_int=500, body='No Bioent specified.')
    

'''
-------------------------------Overview Table---------------------------------------
'''

def make_overview_tables(divided, biorels, bioent=None):
    tables = {}
            
    if divided:
        divided_biorels = divide_biorels(divided)
        
        tables['physical'] = make_overview_table(divided_biorels['physical'], bioent)
        tables['genetic'] = make_overview_table(divided_biorels['genetic'], bioent)
    else:
        tables['aaData'] = make_overview_table(biorels, bioent)
    return tables    

def make_overview_table(biorels, bioent):
    
    def f(biorel, bioent):
        if bioent is not None:
            orig_bioent = bioent
            opp_bioent = biorel.get_opposite(orig_bioent)
        else:
            orig_bioent = biorel.source_bioent
            opp_bioent = biorel.sink_bioent
        return [bioent.name_with_link, opp_bioent.name_with_link, biorel.genetic_evidence_count, biorel.physical_evidence_count, biorel.evidence_count]
        
    return create_simple_table(biorels, f, bioent=bioent) 

def make_overview_row(biorel, evs_for_group, group_term):
    if group_term[1] is not None:
        orig_bioent = group_term[1]
        opp_bioent = biorel.get_opposite(orig_bioent)
    else:
        orig_bioent = biorel.source_bioent
        opp_bioent = biorel.sink_bioent
    divided_evidences = divide_interevidences(evs_for_group)
    total = entry_with_link(str(len(evs_for_group)), biorel.link)
    return [orig_bioent.name_with_link, opp_bioent.name_with_link, len(divided_evidences['genetic']), len(divided_evidences['physical']), total]

    
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_evidence_tables(divided, biorels, bioent=None):
    tables = {}
    interevidences = get_interaction_evidence(biorels)

    if divided:
        divided_evidences = divide_interevidences(interevidences)

        tables['genetic'] = create_simple_table(divided_evidences['genetic'], make_evidence_row, bioent=bioent)
        tables['physical'] = create_simple_table(divided_evidences['physical'], make_evidence_row, bioent=bioent)
        
    else:
        tables['aaData'] = create_simple_table(interevidences, make_evidence_row, bioent)
        
    tables['reference'] = make_reference_list(interevidences)
        
    return tables    

def make_evidence_row(interevidence, bioent=None): 
    if bioent is None:
        bioent1 = interevidence.biorel.source_bioent
        bioent2 = interevidence.biorel.sink_bioent
        direction = interevidence.direction
    else:
        bioent1 = bioent
        bioent2 = interevidence.biorel.get_opposite(bioent1)
        if interevidence.biorel.source_bioent == bioent1:
            direction = interevidence.direction
        else:
            direction = reverse_direction(interevidence.direction)
    
    reference = ''
    if interevidence.reference is not None:
        reference = interevidence.reference.name_with_link
    
     
    return [bioent1.name_with_link, bioent2.name_with_link, 
            interevidence.experiment_type, interevidence.annotation_type, direction, interevidence.phenotype,
            interevidence.modification, interevidence.source, reference]
    
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
    return {'id':get_id(obj), 'label':obj.name, 'link':obj.link, 'evidence':evidence_count, 'sub_type':sub_type}

def create_interaction_edge(obj, source_obj, sink_obj, evidence_count):
    return { 'id': get_id(obj), 'target': get_id(source_obj), 'source': get_id(sink_obj), 'label': obj.name, 'link':obj.link, 
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

    bioents.update([interaction.get_opposite(bioent) for interaction in get_biorels('INTERACTION', bioent)])
    bioent_to_evidence.update([(interaction.get_opposite(bioent), interaction.evidence_count) for interaction in bioent.biorelations])

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
        if interaction.evidence_count >= min_evidence_count and interaction.source_bioent_id in node_ids and interaction.sink_bioent_id in node_ids:
            source_bioent = id_to_bioent[interaction.source_bioent_id]
            sink_bioent = id_to_bioent[interaction.sink_bioent_id]
            edges.append(create_interaction_edge(interaction, source_bioent, sink_bioent, interaction.evidence_count)) 
        
    return {'dataSchema':interaction_schema, 'data': {'nodes': nodes, 'edges': edges}, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_cutoff}

'''
-------------------------------Utils---------------------------------------
'''  
def get_id(bio):
    return bio.type + str(bio.id)

def divide_interevidences(interevidences):
    physical = [interevidence for interevidence in interevidences if interevidence.interaction_type == 'physical']
    genetic = [interevidence for interevidence in interevidences if interevidence.interaction_type == 'genetic']
    return {'physical':physical, 'genetic':genetic}

def divide_biorels(biorels):
    physical = [biorel for biorel in biorels if biorels.physical_evidence_count > 0]
    genetic = [biorel for biorel in biorels if biorels.genetic_evidence_count > 0]
    return {'physical':physical, 'genetic':genetic}

        
