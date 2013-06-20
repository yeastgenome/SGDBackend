'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import add_link
from pyramid.response import Response
from pyramid.view import view_config
from query import get_biorels, get_interactions, get_bioent, get_reference_id, \
    get_genetic_interaction_evidence, get_physical_interaction_evidence, get_biorel_id
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
        interevidences = get_interaction_evidence(biorel_id=biorel_id)
        return make_evidence_tables(True, interevidences) 
        
    elif 'bioent' in request.GET:
        #Need an interaction evidence table based on a bioent
        bioent_name = request.GET['bioent']
        bioent = get_bioent(bioent_name, 'LOCUS')
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        interevidences = get_interaction_evidence(bioent_id=bioent.id)
        return make_evidence_tables(True, interevidences, bioent) 
    
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
    

'''
-------------------------------Overview Table---------------------------------------
'''

def make_overview_tables(genetic, physical, bioent=None):
    tables = {}
            
    tables['aaData'] = make_overview_table(genetic, physical, bioent)
    return tables    

def make_overview_table(genetic, physical, bioent):
    inters_to_counts = dict()
    
    for x in genetic:
        inters = tuple(x.bioentities)
        if inters in inters_to_counts:
            genetic_count, physical_count = inters_to_counts[inters]
            inters_to_counts[inters] = (x.evidence_count, physical_count)
        else:
            inters_to_counts[inters] = (x.evidence_count, 0) 
           
    for x in physical:
        inters = tuple(x.bioentities)
        if inters in inters_to_counts:
            genetic_count, physical_count = inters_to_counts[inters]
            inters_to_counts[inters] = (genetic_count, x.evidence_count)
        else:
            inters_to_counts[inters] = (0, x.evidence_count) 
                
    def f(inters, bioent):
        if len(inters) == 1:
            orig_bioent_link = inters[0].name_with_link
            opp_bioent_link = inters[0].name_with_link
        elif len(inters) > 2:
            if bioent is not None:
                orig_bioent = bioent
            else:
                orig_bioent = inters[0]
            orig_bioent_link = orig_bioent.name_with_link
            opp_bioents = list(inters)
            opp_bioents.remove(orig_bioent)
            opp_bioent_link = ', '.join([x.name_with_link for x in opp_bioents])
        else:
            if bioent is not None:
                orig_bioent = bioent
            else:
                orig_bioent = inters[0]
            orig_bioent_link = orig_bioent.name_with_link
            opp_bioents = list(inters)
            opp_bioents.remove(orig_bioent)
            opp_bioent_link = opp_bioents[0].name_with_link
            
        genetic_count = inters_to_counts[inters][0]
        physical_count = inters_to_counts[inters][1]
        total_count = genetic_count + physical_count
        return [orig_bioent_link, opp_bioent_link, genetic_count, physical_count, total_count]
        
    return create_simple_table(inters_to_counts.keys(), f, bioent=bioent) 

def make_overview_row(biorel, evs_for_group, group_term):
    if group_term[1] is not None:
        orig_bioent = group_term[1]
        opp_bioent = biorel.get_opposite(orig_bioent)
    else:
        orig_bioent = biorel.source_bioent
        opp_bioent = biorel.sink_bioent
    divided_evidences = divide_interevidences(evs_for_group)
    total = add_link(str(len(evs_for_group)), biorel.link)
    return [orig_bioent.name_with_link, opp_bioent.name_with_link, len(divided_evidences['genetic']), len(divided_evidences['physical']), total]

    
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_evidence_tables(divided, interevidences, bioent=None):
    tables = {}

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
        
    phenotype = None
    if interevidence.qualifier is not None or interevidence.observable is not None:
        phenotype = ''
        if interevidence.qualifier is not None:
            phenotype = interevidence.qualifier + ' ' 
        if interevidence.observable is not None:
            phenotype = phenotype + interevidence.observable
     
    return [bioent1.name_with_link, bioent2.name_with_link, 
            interevidence.experiment_type, interevidence.annotation_type, direction, phenotype,
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

