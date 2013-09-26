'''
Created on Sep 20, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from sgdbackend.cache import get_cached_bioent, get_cached_strain
from sgdbackend.obj_to_json import domain_to_json
from sgdbackend.utils import create_simple_table
from sgdbackend_query.query_bioent import get_domain_evidence

@view_config(route_name='protein_domain_details', renderer="jsonp")
def protein_domain_details(request):
    #Need protein domains based on a bioent
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    
    bioent = get_cached_bioent(identifier, entity_type)
    
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
    
    if bioent['bioent_type'] == 'PROTEIN':
        protein = bioent
    else:
        protein = get_cached_bioent(bioent['format_name'] + 'P', 'PROTEIN')
        if protein is None:
            return None
    
    domain_evidences = [x for x in get_domain_evidence(protein['id']) if x.domain.display_name != 'seg' ]
    return make_evidence_table(domain_evidences)
    
def make_evidence_table(domain_evidences):
    return create_simple_table(domain_evidences, make_evidence_row) 

def make_evidence_row(domain_evidence): 
    return {    'start': domain_evidence.start,
                'end': domain_evidence.end,
                'evalue': domain_evidence.evalue,
                'status': domain_evidence.status,
                'date_of_run': domain_evidence.date_of_run,
                'protein': get_cached_bioent(domain_evidence.protein_id),
                'domain': domain_to_json(domain_evidence.domain),
                'source': domain_evidence.source,
                'strain': get_cached_strain(domain_evidence.strain_id)
                }