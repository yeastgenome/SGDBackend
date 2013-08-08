from pyramid.response import Response
from pyramid.view import view_config
from query import get_chemical
from query.query_biocon import get_biocon
from query.query_bioent import get_bioent, get_bioents, get_all_bioents, \
    get_bioent_id, get_bioent_from_id
from query.query_reference import get_references


@view_config(route_name='bioent', renderer='json')
def bioent(request):
    bioent_name = request.matchdict['bioent']
    bioent = get_bioent(bioent_name, 'LOCUS')
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
        
    bioent_json = {
                    'format_name': bioent.format_name,
                    'bioent_type': bioent.bioent_type,
                    'display_name': bioent.display_name, 
                    'link': bioent.link,
                    'bioent_id': bioent.id
                    }
    return bioent_json

@view_config(route_name='all_bioents', renderer='json')
def all_bioents(request):
    min_id = int(request.GET['min'])
    max_id = int(request.GET['max'])
    bioents = get_all_bioents(min_id, max_id)
    bioent_json = []
    for bioent in bioents:
        bioent_json.append({'format_name': bioent.format_name,
                            'bioent_type': bioent.bioent_type,
                            'display_name': bioent.display_name, 
                            'link': bioent.link,
                            'bioent_id': bioent.id
                            })
    return bioent_json

@view_config(route_name='locus', renderer='json')
def locus(request):
    bioent_name = request.matchdict['bioent']
    bioent = get_bioent(bioent_name, 'LOCUS')
    if bioent is None:
        return Response(status_int=500, body='Locus could not be found.')
    
    bioent_json = {
                   'display_name': bioent.display_name, 
                   'format_name': bioent.format_name,
                   'full_name': bioent.full_name,
                   'description': bioent.description,
                   
                   'source': bioent.source,
                   'attribute': bioent.attribute,
                   'name_description': bioent.name_description,
                   'qualifier': bioent.qualifier,
                   'bioent_type': bioent.bioent_type,
                   'aliases': bioent.alias_str,
                   'wiki_name_with_link': bioent.wiki_name_with_link,
    
                   }
    return bioent_json 

@view_config(route_name='biocon', renderer='json')
def biocon(request):
    biocon_name = request.matchdict['biocon']
    biocon_type = request.matchdict['biocon_type'].upper()
    biocon = get_biocon(biocon_name, biocon_type)
    if biocon is None:
        return Response(status_int=500, body='Biocon could not be found.')
        
    biocon_json = {
                    'format_name': biocon.format_name,
                    'display_name': biocon.display_name, 
                    'name_with_link': biocon.name_with_link,
                    }
    return biocon_json

@view_config(route_name='chemical', renderer='json')
def chemical(request):
    chemical_name = request.matchdict['chemical']
    chemical = get_chemical(chemical_name)
    if chemical is None:
        return Response(status_int=500, body='Chemical could not be found.')
    
    chemical_json = {
                     'format_name': chemical.format_name,
                     'display_name': chemical.display_name,
                     'name_with_link': chemical.name_with_link,
                     'aliases': chemical.alias_str
                     }
    return chemical_json

@view_config(route_name='bioent_list', renderer='json')
def bioent_list_view(request):
    bioent_ids = set(request.POST['bioent_ids'].split(','))
    bioents = get_bioents(bioent_ids=bioent_ids)
    if bioents is None:
        return Response(status_int=500, body='Bioents could not be found.')
    
    bioents_json = []
    for bioent in bioents:
        bioents_json.append({
                    'id': bioent.id,
                    'format_name': bioent.format_name,
                    'display_name': bioent.display_name, 
                    'name_with_link': bioent.name_with_link,
                    'description': bioent.description
                    })
    return bioents_json

@view_config(route_name='reference_list', renderer='json')
def reference_list_view(request):
    reference_ids = set(request.POST['reference_ids'].split(','))
    references = get_references(reference_ids=reference_ids)
    if references is None:
        return Response(status_int=500, body='References could not be found.')
    
    references_json = []
    for reference in references:     
        journal_name = None
        journal_name_abbrev = None
        issn = None
        essn = None
        publisher = None
        
        book_title = None
        volume_title = None
        isbn = None
        total_pages = None
        publisher_location = None
        
        if reference.journal is not None:
            publisher = reference.journal.publisher
            journal_name = reference.journal.full_name
            journal_name_abbrev = reference.journal.abbreviation
            issn = reference.journal.issn
            essn = reference.journal.essn
            
        if reference.book is not None:
            publisher = reference.book.publisher
            book_title = reference.book.title
            volume_title = reference.book.volume_title
            isbn = reference.book.isbn
            total_pages = reference.book.total_pages
            publisher_location = reference.book.publisher_location

        json_ref = {
                    'source': reference.source,
                    'status': reference.status,
                    'pubmed_id': reference.pubmed_id, 
                    'pdf_status': reference.pdf_status,
                    'year': reference.year,
                    'date_published': reference.date_published,
                    'date_revised': reference.date_revised,
                    'issue': reference.issue,
                    'page': reference.page,
                    'volume': reference.volume,
                    'title': reference.title,
                    'abstract': reference.abstract,
                    'journal_name': journal_name,
                    'journal_name_abbrev': journal_name_abbrev,
                    'issn': issn,
                    'essn': essn,
                    'publisher': publisher,
                    'book_title': book_title,
                    'volume_title': volume_title,
                    'isbn': isbn,
                    'total_pages': total_pages,
                    'publisher_location': publisher_location,
                    'authors': list(reference.author_names),
                    'reftypes': list(reference.reftype_names)
                    }
        references_json.append(json_ref)
    return references_json


def get_bioent_id_from_repr(bioent_repr):
    bioent_id = None
    try:
        bioent_id = int(bioent_repr)
    except ValueError:
        bioent_id = get_bioent_id(bioent_repr, 'LOCUS')
    return bioent_id

def get_bioent_from_repr(bioent_repr):
    bioent = None
    try:
        bioent_id = int(bioent_repr)
        bioent = get_bioent_from_id(bioent_id)
    except ValueError:
        bioent = get_bioent(bioent_repr, 'LOCUS')
    return bioent




