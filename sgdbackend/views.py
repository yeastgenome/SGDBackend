from pyramid.response import Response
from pyramid.view import view_config
from sgdbackend.cache import get_cached_bioent, id_to_bioent
from sgdbackend_query.query_reference import get_reference_bibs


@view_config(route_name='bioentity', renderer='json')
def bioentity(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
    return bioent

@view_config(route_name='all_bioents', renderer='json')
def all_bioents(request):
    min_id = None
    max_id = None
    if 'min' in request.GET and 'max' in request.GET:
        min_id = int(request.GET['min'])
        max_id = int(request.GET['max'])
    bioents = {}
    for bioent in id_to_bioent.values():
        bioent_id = bioent['id']
        if min_id is not None:
            if bioent_id >= min_id and bioent_id < max_id:
                bioents[bioent_id] = bioent
        else:
            bioents[bioent_id] = bioent
    return bioents.values()


@view_config(route_name='bioent_list', renderer='jsonp')
def bioent_list_view(request):
    bioent_ids = request.json_body['bioent_ids']
    bioents = []
    for bioent_id in bioent_ids:
        bioent = get_cached_bioent(str(bioent_id), bioent_type='locus')
        if bioent is not None:
            bioents.append(bioent)
    return bioents

@view_config(route_name='reference_list', renderer='jsonp')
def reference_list_view(request):
    reference_ids = request.json_body['reference_ids']
    print reference_ids
    ref_bibs = get_reference_bibs(reference_ids=reference_ids)
    if ref_bibs is None:
        return Response(status_int=500, body='References could not be found.')
    
    references_json = [ref_bib.bib_entry for ref_bib in ref_bibs]
    return references_json







