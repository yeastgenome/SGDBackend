'''
Created on Mar 19, 2013

@author: kpaskov
'''
from datetime import datetime
from pyramid.response import Response
from pyramid.view import view_config
from query import search, get_objects, typeahead
from sqlalchemy.exc import DBAPIError
import math

results_per_page = 20
    
@view_config(route_name='search_results', renderer='jsonp')
def search_results(request):
    try:
        keywords = request.GET['keyword'].lower().split()
        
        biotype = request.GET['bio_type']
        if biotype == 'all':
            biotype = None
        page = int(request.GET['page'])
        
        begin = datetime.now()
        search_results = search(keywords, biotype)
        end = datetime.now()
        print 'search: ' + str(end-begin)
        
        num_results = int(len(search_results))
        num_pages = int(math.ceil(1.0*num_results/results_per_page))
        
        begin = datetime.now()
        search_results = sort_results(search_results)
        counts = count_results(search_results)
        end = datetime.now()
        print 'sort: ' + str(end-begin)
        
        search_results = search_results[page*results_per_page:(page+1)*results_per_page]
        
        begin = datetime.now()
        search_result_objs = get_objects(search_results)
        end = datetime.now()
        print 'get objects: ' + str(end-begin)
        
        search_result_jsons = [[x.search_entry_type, x.search_entry_title, x.search_description, x.search_additional] for x in search_result_objs]
    except DBAPIError:
        return Response("Error.", content_type='text/plain', status_int=500)
    return {'results': search_result_jsons, 'num_pages':num_pages, 'num_results':num_results, 'counts':counts}

@view_config(route_name='typeahead', renderer="jsonp")
def typeahead_view(request):
    try:
        search_str = request.POST.items()[0][1].upper()
        possible = typeahead(search_str)
        full_names = [p.full_name for p in possible]
        return sorted(full_names)
    except DBAPIError:
        return ['Error']
    
source_priorities = {'NAME':1, 'GENE_NAME':0, 'ALIAS':2, 'AUTHOR_YEAR':3, 'TITLE': 4, 'CITATION': 5, 'NAME_DESC':6, 'DESCRIPTION':7, 'ABSTRACT':8,
                     'PUBMED_ID':10, 'DOI':11}
bio_type_priorities = {'LOCUS':0, 'GO':.1, 'PHENOTYPE':.2, 'REFERENCE':.3, 'PROTEIN':.4, 'SEQUENCE':.5, 'TRANSCRIPT':.6}

def sort_results(search_results):
    return sorted(search_results, key=lambda x: source_priorities[x.source] + bio_type_priorities[x.bio_type])

def count_results(search_results):
    counts = {}
    for key in bio_type_priorities.keys():
        counts[key] = len([x for x in search_results if x.bio_type==key])
    return counts
    
    
    
    