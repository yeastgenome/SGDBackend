from pyramid.response import Response
from pyramid.view import view_config
from query import get_reference, get_author, get_chemical, get_bioent, \
    get_biocon, get_biorel, get_author_id, get_assoc_reference
from utils.utils import make_reference_list


@view_config(route_name='bioent', renderer='json')
def bioent(request):
    bioent_name = request.matchdict['bioent']
    bioent_type = request.matchdict['bioent_type'].upper()
    bioent = get_bioent(bioent_name, bioent_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
        
    bioent_json = {
                    'format_name': bioent.format_name,
                    'display_name': bioent.display_name, 
                    'name_with_link': bioent.name_with_link,
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

@view_config(route_name='biorel', renderer='json')
def biorel(request):
    biorel_name = request.matchdict['biorel']
    biorel_type = request.matchdict['biorel_type'].upper()
    biorel = get_biorel(biorel_name, biorel_type)
    if biorel is None:
        return Response(status_int=500, body='Biorel could not be found.')
        
    biorel_json = {
                    'format_name': biorel.format_name,
                    'display_name': biorel.display_name, 
                    'name_with_link': biorel.name_with_link,
                    'description': biorel.description
                    }
    return biorel_json

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

@view_config(route_name='reference', renderer='json')
def reference_view(request):
    ref_name = request.matchdict['reference']
    reference = get_reference(ref_name)   
    if reference is None:
        return Response(status_int=500, body='Reference could not be found.') 
    
    reference_json = {
                     'format_name': reference.format_name,
                     'display_name': reference.display_name,
                     'name_with_link': reference.name_with_link,
                     'abstract': reference.abstract,
                     'pubmed_id': reference.pubmed_id_with_link,
                     'authors': reference.author_str,
                     'reftypes': reference.reftype_str,
                     'related_references': reference.related_ref_str,
                     'urls': reference.url_str,
                     'citation': reference.citation_db
                     }
    return reference_json

@view_config(route_name='author', renderer='json')
def author_view(request):
    author_name = request.matchdict['author']
    author = get_author(author_name)
    if author is None:
            return Response(status_int=500, body='Author could not be found.') 
        
    author_json = {
                    'format_name': author.format_name,
                     'display_name': author.display_name,
                     'name_with_link': author.name_with_link
                   }
    return author_json

@view_config(route_name='assoc_references', renderer='jsonp')
def assoc_references(request):
    if 'author' in request.GET:
        #Need associated references for an author.
        author_name = request.GET['author']
        author_id = get_author_id(author_name)
        if author_id is None:
            return Response(status_int=500, body='Author could not be found.')
        references = get_assoc_reference(author_id=author_id)
        return make_reference_list(references=references)
    else:
        return Response(status_int=500, body='No Author specified.')



