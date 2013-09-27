'''
Created on Mar 15, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from sgdbackend.cache import get_cached_bioent, get_cached_experiment, \
    get_cached_reference, get_cached_strain
from sgdbackend.obj_to_json import paragraph_to_json
from sgdbackend.utils import create_simple_table, make_reference_list
from sgdbackend_query import get_paragraph
from sgdbackend_query.query_evidence import get_regulation_evidence
from sgdbackend_query.query_interaction import get_regulation_family

@view_config(route_name='regulation_overview', renderer='jsonp')
def regulation_overview(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body= entity_type + ' ' + str(identifier) + ' could not be found.')
    bioent_id = bioent['id']
    overview = {}
    
    paragraph = get_paragraph(bioent_id, 'REGULATION')
    if paragraph is not None:
        overview['paragraph'] = paragraph_to_json(paragraph)
    regevidences = get_regulation_evidence(bioent_id=bioent_id)
    target_count = len(set([regevidence.bioentity2_id for regevidence in regevidences if regevidence.bioentity1_id==bioent_id]))
    regulator_count = len(set([regevidence.bioentity1_id for regevidence in regevidences if regevidence.bioentity2_id==bioent_id]))
    
    overview['target_count'] = target_count
    overview['regulator_count'] = regulator_count
    return overview

@view_config(route_name='regulation_details', renderer='jsonp')
def regulation_details(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
        
    regevidences = get_regulation_evidence(bioent_id=bioent['id'])
    return make_evidence_tables(True, regevidences, bioent['id']) 
    
@view_config(route_name='regulation_references', renderer="jsonp")
def regulation_references(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
    return make_reference_list(['REGULATION'], bioent['id'])

@view_config(route_name='regulation_graph', renderer="jsonp")
def regulation_graph(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
    return create_regulation_graph(bioent['id'])

    
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_evidence_tables(divided, regevidences, bioent_id):
    tables = {}

    if divided:
        target_regevidences = [regevidence for regevidence in regevidences if regevidence.bioentity1_id==bioent_id]
        regulator_regevidences = [regevidence for regevidence in regevidences if regevidence.bioentity2_id==bioent_id]
        
        tables['targets'] = create_simple_table(target_regevidences, make_evidence_row, bioent_id=bioent_id)
        tables['regulators'] = create_simple_table(regulator_regevidences, make_evidence_row, bioent_id=bioent_id)
        
    else:
        tables = create_simple_table(regevidences, make_evidence_row, bioent_id=bioent_id)
        
    return tables    

def make_evidence_row(regevidence, bioent_id=None): 
    if bioent_id is not None:
        if regevidence.bioentity1_id == bioent_id:
            bioent1_id = bioent_id
            bioent2_id = regevidence.bioentity2_id
        else:
            bioent1_id = bioent_id
            bioent2_id = regevidence.bioentity1_id
    else:
        bioent1_id = regevidence.bioentity1_id
        bioent2_id = regevidence.bioentity2_id

    reference_id = regevidence.reference_id 
    experiment_id = regevidence.experiment_id
    strain_id = regevidence.strain_id
        
    return {'bioent1': get_cached_bioent(bioent1_id),
                'bioent2': get_cached_bioent(bioent2_id),
                'reference': get_cached_reference(reference_id),
                'experiment': get_cached_experiment(experiment_id),
                'strain': get_cached_strain(strain_id),
                'source': regevidence.source,
                'conditions': regevidence.conditions
                }

'''
-------------------------------Graph---------------------------------------
'''  

def create_regulation_node(bioent_id, bioent_name, bioent_link, is_focus, total_ev_count, class_type):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent_id), 'name':bioent_name, 'link': bioent_link, 
                    'sub_type':sub_type, 'evidence': total_ev_count, 'class_type': class_type}}

def create_regulation_edge(interaction_id, bioent1_id, bioent2_id, total_ev_count):
    return {'data':{'source': 'Node' + str(bioent1_id), 'target': 'Node' + str(bioent2_id), 'evidence': total_ev_count}}
    
def create_regulation_graph(bioent_id):
    regulation_families = get_regulation_family(bioent_id)
    
    id_to_node = {}
    edges = []
    min_evidence_count = None
    max_evidence_count = 0
    max_target_count = 0
    max_regulator_count = 0
    bioent_id_to_evidence_count = {}
    bioent_id_to_class = {}
    
    for regulation_family in regulation_families:
        evidence_count = regulation_family.evidence_count
           
        bioent1_id = regulation_family.bioentity1_id
        bioent2_id = regulation_family.bioentity2_id
        if bioent1_id==bioent_id or bioent2_id==bioent_id:
            if min_evidence_count is None or evidence_count < min_evidence_count:
                min_evidence_count = evidence_count
            if evidence_count > max_evidence_count:
                max_evidence_count = evidence_count
            
            if bioent1_id==bioent_id and evidence_count > max_target_count:
                max_target_count = evidence_count
            if bioent2_id==bioent_id and evidence_count > max_regulator_count:
                max_regulator_count = evidence_count
            
            if bioent1_id not in bioent_id_to_evidence_count:
                bioent_id_to_evidence_count[bioent1_id] = evidence_count
            else:
                bioent_id_to_evidence_count[bioent1_id] = max(bioent_id_to_evidence_count[bioent1_id], evidence_count)
                
            if bioent2_id not in bioent_id_to_evidence_count:
                bioent_id_to_evidence_count[bioent2_id] = evidence_count
            else:
                bioent_id_to_evidence_count[bioent2_id] = max(bioent_id_to_evidence_count[bioent2_id], evidence_count)
                
            bioent_id_to_class[bioent1_id] = 'REGULATOR'
            bioent_id_to_class[bioent2_id] = 'TARGET'
                                            
    for regulation_family in regulation_families:
        bioent1_id = regulation_family.bioentity1_id
        bioent2_id = regulation_family.bioentity2_id
    
        if bioent1_id not in id_to_node:
            bioent1 = get_cached_bioent(bioent1_id)
            evidence_count = bioent_id_to_evidence_count[bioent1_id]
            class_type = bioent_id_to_class[bioent1_id]
            id_to_node[bioent1_id] = create_regulation_node(bioent1_id, bioent1['display_name'], 
                                                            bioent1['link'], bioent1_id==bioent_id, evidence_count, class_type=class_type)
        if bioent2_id not in id_to_node:
            bioent2 = get_cached_bioent(bioent2_id)
            evidence_count = bioent_id_to_evidence_count[bioent2_id]
            class_type = bioent_id_to_class[bioent2_id]
            id_to_node[bioent2_id] = create_regulation_node(bioent2_id, bioent2['display_name'], 
                                                            bioent2['link'], bioent2_id==bioent_id, evidence_count, class_type=class_type)
        edges.append(create_regulation_edge(regulation_family.id, bioent1_id, bioent2_id, 
                                             regulation_family.evidence_count))
            
    
    return {'nodes': id_to_node.values(), 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_count,
            'max_target_cutoff': max_target_count, 'max_regulator_cutoff': max_regulator_count}



