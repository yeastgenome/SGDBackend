'''
Created on Jun 7, 2013

@author: kpaskov
'''
#from pyramid.response import Response
#from pyramid.view import view_config
#from query.query_reference import get_reference, get_author, get_author_id, \
#    find_bioentities, get_assoc_reference
#from sgdbackend.graph_views import create_graph
#from sgdbackend.utils import make_reference_list
#
#@view_config(route_name='reference', renderer='json')
#def reference_view(request):
#    ref_name = request.matchdict['reference']
#    reference = get_reference(ref_name)   
#    if reference is None:
#        return Response(status_int=500, body='Reference could not be found.') 
#    
#    reference_json = {
#                     'format_name': reference.format_name,
#                     'display_name': reference.display_name,
#                     'name_with_link': reference.name_with_link,
#                     'abstract': add_bioent_hyperlinks(reference.abstract),
#                     'pubmed_id': reference.pubmed_id_with_link,
#                     'authors': reference.author_str,
#                     'reftypes': reference.reftype_str,
#                     'related_references': reference.related_ref_str,
#                     'urls': reference.url_str,
#                     'citation': reference.citation_db
#                     }
#    return reference_json
#
#@view_config(route_name='reference_graph', renderer="jsonp")
#def reference_graph(request):
#    if 'reference' in request.GET:
#        #Need a reference graph based on a reference
#        reference_name = request.GET['reference']
#        reference = get_reference(reference_name)
#        if reference is None:
#            return Response(status_int=500, body='Reference could not be found.')
#        
#        evidence_filter = lambda x: x.evidence_type != 'BIOENT_EVIDENCE' or x.topic=='Primary Literature'
#        l1_filter = lambda x, y: True
#        l2_filter = lambda x, y: len(y) > 1
#        return create_graph(['BIOENTITY'], ['REFERENCE'], evidence_filter, l1_filter, l2_filter, seed_refs=[reference]) 
#
#    else:
#        return Response(status_int=500, body='No Reference specified.')
#
#@view_config(route_name='author', renderer='json')
#def author_view(request):
#    author_name = request.matchdict['author']
#    author = get_author(author_name)
#    if author is None:
#            return Response(status_int=500, body='Author could not be found.') 
#        
#    author_json = {
#                    'format_name': author.format_name,
#                     'display_name': author.display_name,
#                     'name_with_link': author.name_with_link
#                   }
#    return author_json
#
#@view_config(route_name='assoc_references', renderer='jsonp')
#def assoc_references(request):
#    if 'author' in request.GET:
#        #Need associated references for an author.
#        author_name = request.GET['author']
#        author_id = get_author_id(author_name)
#        if author_id is None:
#            return Response(status_int=500, body='Author could not be found.')
#        references = get_assoc_reference(author_id=author_id)
#        return make_reference_list(references=references)
#    else:
#        return Response(status_int=500, body='No Author specified.')
#


#def add_bioent_hyperlinks(text):
#    if text is None:
#        return None
#    bioentities = find_bioentities(text)
#    word_to_link = {}
#    for name, bioent in bioentities.iteritems():
#        word_to_link[name.upper()] = bioent.link
#        
#    words = text.split()
#    for i in range(0, len(words)):
#        upper = words[i].upper()
#        if upper in word_to_link:
#            word = words[i]
#            words[i] = "<a href='" + word_to_link[upper] + "'>" + word + "</a>"
#        else:
#            #remove_punc = upper.translate(string.maketrans("",""), string.punctuation)
#            remove_punc = upper
#            if remove_punc in word_to_link:
#                link = word_to_link[remove_punc]
#                index = words[i].upper().find(remove_punc)
#                if index >= 0:
#                    word = words[i]
#                    words[i] = word[:index] + add_link(word[index:index+len(remove_punc)], link) + word[index+len(remove_punc):]
#            
#    return ' '.join([x for x in words])
