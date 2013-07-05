'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import add_link
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
        resources = get_resources('Interaction Resources', bioent_id=bioent_id)
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
    inters = tuple(interevidence.biorel.bioentities)
    if len(inters) == 1:
        orig_bioent_link = inters[0].name_with_link
        opp_bioent_link = inters[0].name_with_link
        direction = 'Bait/Hit'
    elif len(inters) > 2:
        if bioent is not None:
            orig_bioent = bioent
        else:
            orig_bioent = inters[0]
        orig_bioent_link = orig_bioent.name_with_link
        opp_bioents = list(inters)
        opp_bioents.remove(orig_bioent)
        opp_bioent_link = ', '.join([x.name_with_link for x in opp_bioents])
        
        pos = list(interevidence.biorel.bioentities).index(orig_bioent)
        bait_hit_desig = interevidence.bait_hit.split('-')
        bait_hit_desig.pop(pos)
        direction = ', '.join(bait_hit_desig)
    else:
        if bioent is not None:
            orig_bioent = bioent
        else:
            orig_bioent = inters[0]
        orig_bioent_link = orig_bioent.name_with_link
        opp_bioents = list(inters)
        opp_bioents.remove(orig_bioent)
        opp_bioent_link = opp_bioents[0].name_with_link
        pos = list(interevidence.biorel.bioentities).index(orig_bioent)
        
        bait_hit_desig = interevidence.bait_hit.split('-')
        bait_hit_desig.pop(pos)
        direction = ', '.join(bait_hit_desig)
    
    reference = ''
    if interevidence.reference is not None:
        reference = interevidence.reference.name_with_link 
    experiment = ''
    if interevidence.experiment is not None:
        experiment = interevidence.experiment.name_with_link
        
    phenotype = ''
    if interevidence.evidence_type == 'GENETIC_INTERACTION_EVIDENCE' and interevidence.phenotype is not None:
        phenotype = interevidence.phenotype.name_with_link
    modification = ''
    if interevidence.evidence_type == 'PHYSICAL_INTERACTION_EVIDENCE' and interevidence.modification is not None:
        modification = interevidence.modification
        
    notes = [note.note for note in interevidence.notes]
    if len(notes) == 0:
        note = None
    else:
        note = '; '.join(notes)
     
    return [None, orig_bioent_link, opp_bioent_link, 
            experiment, interevidence.annotation_type, direction, phenotype,
            modification, interevidence.source, reference, note]
    
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

