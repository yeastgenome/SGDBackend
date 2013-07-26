'''
Created on Mar 15, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from query import get_resources
from query.query_bioent import get_bioent, get_bioent_id
from query.query_evidence import get_genetic_interaction_evidence, \
    get_physical_interaction_evidence
from query.query_interaction import get_interactions, get_interaction_family
from query.query_reference import get_reference_id
from sgdbackend.utils import create_simple_table, make_reference_list
from sgdbackend.venn import calc_venn_measurements



@view_config(route_name='interaction_overview_table', renderer='jsonp')
def interaction_overview_table(request):
    if 'bioent' in request.GET:
        #Need an interaction overview table based on a bioent
        bioent_name = request.GET['bioent']
        bioent = get_bioent(bioent_name, 'LOCUS')
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        genetic = get_interactions('GENETIC_INTERACTION', bioent.id)
        physical = get_interactions('PHYSICAL_INTERACTION', bioent.id)
        return make_overview_table(genetic, physical, bioent) 
    
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
        return make_overview_table(genetic, physical) 

    else:
        return Response(status_int=500, body='No Bioent or Reference specified.')


@view_config(route_name='interaction_evidence_table', renderer='jsonp')
def interaction_evidence_table(request):
    if 'bioent' in request.GET:
        #Need an interaction evidence table based on a bioent
        bioent_name = request.GET['bioent']
        bioent = get_bioent(bioent_name, 'LOCUS')
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        genetic_interevidences = get_genetic_interaction_evidence(bioent_id=bioent.id)
        physical_interevidences = get_physical_interaction_evidence(bioent_id=bioent.id)
        return make_evidence_tables(False, genetic_interevidences, physical_interevidences, bioent) 
    
    else:
        return Response(status_int=500, body='No Bioent specified.')
    
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
    
    return {'aaData': create_simple_table(all_inters, f, bioent=bioent),
            'venn':[r, s, x]}

    
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
        tables['aaData'] = create_simple_table(all_interevidences, make_evidence_row, bioent=bioent)
        
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
    note=interevidence.note
        
    if interevidence.evidence_type == 'GENETIC_INTERACTION_EVIDENCE':
        phenotype_link = ''
        if interevidence.phenotype_id is not None:
            phenotype_link = interevidence.phenotype_name_with_link
        return [None, orig_bioent_link, opp_bioent_link, 'Genetic',
            experiment_link, interevidence.annotation_type, direction, None, phenotype_link,
            interevidence.source, reference_link, note]
        
    elif interevidence.evidence_type == 'PHYSICAL_INTERACTION_EVIDENCE':
        modification = ''
        if interevidence.modification is not None:
            modification = interevidence.modification
        return [None, orig_bioent_link, opp_bioent_link, 'Physical',
            experiment_link, interevidence.annotation_type, direction,
            modification, None, interevidence.source, reference_link, note]
    else:
        return None

'''
-------------------------------Graph---------------------------------------
'''  
    
interaction_schema = {'nodes': [ { 'name': "label", 'type': "string" },  
                         { 'name': "link", 'type': "string" },
                         {'name':'evidence', 'type':'integer'},
                         {'name':'sub_type', 'type':'string'}],
                'edges': [{'name':'evidence', 'type':'integer'}]}

def create_interaction_node(bioent_id, bioent_name, bioent_link, is_focus, evidence_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'id':'Node' + str(bioent_id), 'label':bioent_name, 'link': bioent_link, 'evidence':evidence_count, 'sub_type':sub_type}

def create_interaction_edge(interaction_id, bioent1_id, bioent2_id, evidence_count):
    return { 'id': 'Edge' + str(interaction_id), 'target': 'Node' + str(bioent1_id), 'source': 'Node' + str(bioent2_id), 
            'evidence':evidence_count}  
    
def create_interaction_graph(bioent):
    bioent_id = bioent.id
    interaction_families = get_interaction_family(bioent_id)
    
    id_to_node = {}
    edges = []
    min_evidence_count = None
    max_evidence_count = None
    bioent_id_to_evidence_count = {}
    
    for interaction_family in interaction_families:
        evidence_count = interaction_family.evidence_count
           
        bioent1_id = interaction_family.bioent1_id
        bioent2_id = interaction_family.bioent2_id
        if bioent1_id==bioent_id or bioent2_id==bioent_id:
            if min_evidence_count is None or evidence_count < min_evidence_count:
                min_evidence_count = evidence_count
            if max_evidence_count is None or evidence_count > max_evidence_count:
                max_evidence_count = evidence_count
            
            if bioent1_id not in bioent_id_to_evidence_count or bioent_id_to_evidence_count[bioent1_id] < evidence_count:
                bioent_id_to_evidence_count[bioent1_id] = evidence_count
            if bioent2_id not in bioent_id_to_evidence_count or bioent_id_to_evidence_count[bioent2_id] < evidence_count:
                bioent_id_to_evidence_count[bioent2_id] = evidence_count    
            
    for interaction_family in interaction_families:
        bioent1_id = interaction_family.bioent1_id
        bioent2_id = interaction_family.bioent2_id
        evidence_count = interaction_family.evidence_count
        if bioent1_id not in id_to_node:
            bioent_name = interaction_family.bioent1_display_name
            bioent_link = interaction_family.bioent1_link
            id_to_node[bioent1_id] = create_interaction_node(bioent1_id, bioent_name, bioent_link, bioent1_id==bioent_id, bioent_id_to_evidence_count[bioent1_id])
        if bioent2_id not in id_to_node:
            bioent_name = interaction_family.bioent2_display_name
            bioent_link = interaction_family.bioent2_link
            id_to_node[bioent2_id] = create_interaction_node(bioent2_id, bioent_name, bioent_link, bioent2_id==bioent_id, bioent_id_to_evidence_count[bioent2_id])
        edges.append(create_interaction_edge(interaction_family.id, bioent1_id, bioent2_id, evidence_count))
            
    
    return {'dataSchema':interaction_schema, 'data': {'nodes': id_to_node.values(), 'edges': edges}, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_count}

'''
-------------------------------Utils---------------------------------------
'''  
def get_id(bio):
    return bio.type + str(bio.id)

