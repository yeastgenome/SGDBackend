from pyramid.response import Response
from pyramid.view import view_config
from sgdbackend.cache import get_cached_bioent, id_to_bioent, \
    get_cached_reference


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
    print request.json_body
    bioent_ids = request.json_body['bioent_ids']
    bioents = []
    for bioent_id in bioent_ids:
        bioent = get_cached_bioent(str(bioent_id), bioent_type='locus')
        if bioent is not None:
            bioents.append(bioent)
    print bioents
    return bioents

@view_config(route_name='reference_list', renderer='json')
def reference_list_view(request):
    reference_ids = set(request.POST['reference_ids'].split(','))
    references = []
    for reference_id in reference_ids:
        references.append(get_cached_reference(reference_id))
    filter(None, references)
    return references
    
#    references_json = []
#    for reference in references:     
#        journal_name = None
#        journal_name_abbrev = None
#        issn = None
#        essn = None
#        publisher = None
#        
#        book_title = None
#        volume_title = None
#        isbn = None
#        total_pages = None
#        publisher_location = None
#        
#        if reference.journal is not None:
#            publisher = reference.journal.publisher
#            journal_name = reference.journal.full_name
#            journal_name_abbrev = reference.journal.abbreviation
#            issn = reference.journal.issn
#            essn = reference.journal.essn
#            
#        if reference.book is not None:
#            publisher = reference.book.publisher
#            book_title = reference.book.title
#            volume_title = reference.book.volume_title
#            isbn = reference.book.isbn
#            total_pages = reference.book.total_pages
#            publisher_location = reference.book.publisher_location
#
#        json_ref = {
#                    'source': reference.source,
#                    'status': reference.status,
#                    'pubmed_id': reference.pubmed_id, 
#                    'pdf_status': reference.pdf_status,
#                    'year': reference.year,
#                    'date_published': reference.date_published,
#                    'date_revised': reference.date_revised,
#                    'issue': reference.issue,
#                    'page': reference.page,
#                    'volume': reference.volume,
#                    'title': reference.title,
#                    'abstract': reference.abstract,
#                    'journal_name': journal_name,
#                    'journal_name_abbrev': journal_name_abbrev,
#                    'issn': issn,
#                    'essn': essn,
#                    'publisher': publisher,
#                    'book_title': book_title,
#                    'volume_title': volume_title,
#                    'isbn': isbn,
#                    'total_pages': total_pages,
#                    'publisher_location': publisher_location,
#                    'authors': list(reference.author_names),
#                    'reftypes': list(reference.reftype_names)
#                    }
#        references_json.append(json_ref)
#    return references_json







