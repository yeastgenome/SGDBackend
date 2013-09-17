'''
Created on Mar 15, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from sgdbackend.cache import get_cached_bioent, get_cached_experiment, \
    get_cached_reference
from sgdbackend.utils import create_simple_table, make_reference_list
from sgdbackend_query.query_evidence import get_regulation_evidence



@view_config(route_name='regulation_overview', renderer='jsonp')
def regulation_overview(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body= entity_type + ' ' + str(identifier) + ' could not be found.')
        
    return None

@view_config(route_name='regulation_details', renderer='jsonp')
def regulation_details(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
        
    regevidences = get_regulation_evidence(bioent_id=bioent['id'])
    return make_evidence_tables(True, regevidences, bioent['id']) 
    
@view_config(route_name='regulation_graph', renderer="jsonp")
def regulation_graph(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')  
    return create_regulation_graph(bioent['id'])
    
@view_config(route_name='regulation_references', renderer="jsonp")
def regulation_references(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
    return make_reference_list(['REGULATION_EVIDENCE'], bioent['id'])

    
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
        
    return {'bioent1': get_cached_bioent(bioent1_id),
                'bioent2': get_cached_bioent(bioent2_id),
                'reference': get_cached_reference(reference_id),
                'experiment': get_cached_experiment(experiment_id),
                'source': regevidence.source,
                'conditions': regevidence.conditions
                }

'''
-------------------------------Graph---------------------------------------
'''  

def create_regulation_node(bioent_id, bioent_name, bioent_link, is_focus, gen_ev_count, phys_ev_count, total_ev_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent_id), 'name':bioent_name, 'link': bioent_link, 
                    'sub_type':sub_type}}

def create_regulation_edge(interaction_id, bioent1_id, bioent2_id, gen_ev_count, phys_ev_count, total_ev_count):
    return {'data':{'target': 'Node' + str(bioent1_id), 'source': 'Node' + str(bioent2_id)}}
    
def create_regulation_graph(bioent_id):
    return {'nodes': None, 'edges': None}


