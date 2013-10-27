'''
Created on Mar 15, 2013

@author: kpaskov
'''
from go_enrichment import query_batter
from model_new_schema.evidence import Goevidence
from sgdbackend_query import get_obj_id, get_evidence, get_conditions
from sgdbackend_query.query_auxiliary import get_biofacts
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_biocon, id_to_bioent, id_to_reference, \
    id_to_source
from sgdbackend_utils.obj_to_json import condition_to_json

'''
-------------------------------Enrichment---------------------------------------
''' 
def make_enrichment(bioent_format_names):
    enrichment_results = query_batter.query_go_processes(bioent_format_names)
    json_format = []
    for enrichment_result in enrichment_results:
        identifier = str(int(enrichment_result[0][3:]))
        goterm_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        if goterm_id is not None:
            goterm = id_to_biocon[goterm_id]
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
    return json_format

'''
-------------------------------Overview---------------------------------------
'''  

def make_overview(bioent_id):
    biofacts = get_biofacts('GO', bioent_id=bioent_id)
    biocons = [id_to_biocon[x.bioconcept_id] for x in biofacts]
    
    process_count = len([x for x in biocons if x['go_aspect'] == 'biological process'])
    compartment_count = len([x for x in biocons if x['go_aspect'] == 'cellular compartment'])
    function_count = len([x for x in biocons if x['go_aspect'] == 'molecular function'])
    
    return {'aspect_counts': {'process': process_count, 'compartment':compartment_count, 'function': function_count}}

    
'''
-------------------------------Details---------------------------------------
'''
    
def make_details(locus_id=None, go_id=None):
    goevidences = get_evidence(Goevidence, bioent_id=locus_id, biocon_id=go_id)
    
    id_to_conditions = {}
    for condition in get_conditions([x.id for x in goevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]
            
    tables = create_simple_table(goevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        
    return tables  

def make_evidence_row(goevidence, id_to_conditions): 
    bioentity_id = goevidence.bioentity_id
    bioconcept_id = goevidence.bioconcept_id
    reference_id = goevidence.reference_id 
    source_id = goevidence.source_id
    with_conditions = None if goevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[goevidence.id] if x.role == 'With']
    from_conditions = None if goevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[goevidence.id] if x.role == 'From']
        
    return {'bioentity': id_to_bioent[bioentity_id],
            'bioconcept': id_to_biocon[bioconcept_id],
            'go_aspect': id_to_biocon[bioconcept_id]['go_aspect'],
            'annotation_type': goevidence.annotation_type,
            'date_last_reviewed': goevidence.date_last_reviews,
            'with': with_conditions,
            'from': from_conditions,
            'reference': id_to_reference[reference_id],
            'source': id_to_source[source_id]
            }
        