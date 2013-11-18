'''
Created on Mar 15, 2013

@author: kpaskov
'''
from go_enrichment import query_batter
from model_new_schema.bioconcept import Bioconceptrelation
from model_new_schema.evidence import Goevidence
from mpmath import sqrt, ceil
from sgdbackend_query import get_obj_id, get_evidence, get_conditions
from sgdbackend_query.query_auxiliary import get_biofacts
from sgdbackend_query.query_misc import get_relations
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_biocon, id_to_bioent
from sgdbackend_utils.obj_to_json import condition_to_json, minimize_json, \
    evidence_to_json

'''
-------------------------------Enrichment---------------------------------------
''' 
def make_enrichment(bioent_ids):
    bioent_format_names = [id_to_bioent[bioent_id]['format_name'] for bioent_id in bioent_ids]
    enrichment_results = query_batter.query_go_processes(bioent_format_names)
    json_format = []
    for enrichment_result in enrichment_results:
        identifier = 'GO:' + str(int(enrichment_result[0][3:]))
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
    
def make_details(locus_id=None, go_id=None, chemical_id=None):
    goevidences = get_evidence(Goevidence, bioent_id=locus_id, biocon_id=go_id, chemical_id=chemical_id)
    
    id_to_conditions = {}
    for condition in get_conditions([x.id for x in goevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]
    
    bp_evidence = [x for x in goevidences if id_to_biocon[x.bioconcept_id]['go_aspect'] == 'biological process']      
    mf_evidence = [x for x in goevidences if id_to_biocon[x.bioconcept_id]['go_aspect'] == 'molecular function']    
    cc_evidence = [x for x in goevidences if id_to_biocon[x.bioconcept_id]['go_aspect'] == 'cellular compartment']    
    tables = {}
    tables['biological_process'] = create_simple_table(bp_evidence, make_evidence_row, id_to_conditions=id_to_conditions)
    tables['molecular_function'] = create_simple_table(mf_evidence, make_evidence_row, id_to_conditions=id_to_conditions)
    tables['cellular_compartment'] = create_simple_table(cc_evidence, make_evidence_row, id_to_conditions=id_to_conditions)
        
    return tables  

def make_evidence_row(goevidence, id_to_conditions): 
    bioentity_id = goevidence.bioentity_id
    bioconcept_id = goevidence.bioconcept_id
    with_conditions = [] if goevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[goevidence.id] if x.role == 'With']
    from_conditions = [] if goevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[goevidence.id] if x.role == 'From']
        
    obj_json = evidence_to_json(goevidence)
    obj_json['bioentity'] = minimize_json(id_to_bioent[bioentity_id], include_format_name=True)
    obj_json['bioconcept'] = minimize_json(id_to_biocon[bioconcept_id])
    obj_json['with'] = with_conditions
    obj_json['from']= from_conditions
    obj_json['code'] = goevidence.go_evidence
    obj_json['method'] = goevidence.annotation_type
    obj_json['qualifier'] = goevidence.qualifier
    obj_json['date_created'] = str(goevidence.date_created)
    return obj_json

'''
-------------------------------Ontology Graph---------------------------------------
''' 

def create_node(biocon, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    else:
        sub_type = biocon['go_aspect']
    return {'data':{'id':'Node' + str(biocon['id']), 'name':biocon['display_name'], 'link': biocon['link'], 
                    'sub_type':sub_type, 'count': int(ceil(sqrt(biocon['count'])))}}

def create_edge(interaction_id, biocon1_id, biocon2_id):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id)}} 

def make_ontology_graph(phenotype_id):
    children = get_relations(Bioconceptrelation, 'GO', parent_ids=[phenotype_id])    
    parents = get_relations(Bioconceptrelation, 'GO', child_ids=[phenotype_id])
    if len(parents) > 0:
        grandparents = get_relations(Bioconceptrelation, 'GO', child_ids=[parent.parent_id for parent in parents])
        greatgrandparents = get_relations(Bioconceptrelation, 'GO', child_ids=[parent.parent_id for parent in grandparents])
        greatgreatgrandparents = get_relations(Bioconceptrelation, 'GO', child_ids=[parent.parent_id for parent in greatgrandparents])
        nodes = []
        nodes.append(create_node(id_to_biocon[phenotype_id], True))
        
        child_ids = set([x.child_id for x in children])
        parent_ids = set([x.parent_id for x in parents])
        parent_ids.update([x.parent_id for x in grandparents])
        parent_ids.update([x.parent_id for x in greatgrandparents])
        parent_ids.update([x.parent_id for x in greatgreatgrandparents])
        
        child_id_to_child = dict([(x, id_to_biocon[x]) for x in child_ids])
        parent_id_to_parent = dict([(x, id_to_biocon[x]) for x in parent_ids])
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['child_count'] > 0])
        viable_ids.update([k for k, v in parent_id_to_parent.iteritems() if v['child_count'] > 0])
        viable_ids.add(phenotype_id)
        
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        nodes.extend([create_node(v, False) for k, v in parent_id_to_parent.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in parents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in greatgrandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in greatgreatgrandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
    else:
        grandchildren = get_relations(Bioconceptrelation, 'GO', parent_ids=[x.child_id for x in children])  
        
        child_ids = set([x.child_id for x in children])
        child_ids.update([x.child_id for x in grandchildren])  
        
        child_id_to_child = dict([(x, id_to_biocon[x]) for x in child_ids])
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['child_count'] > 0])
        viable_ids.add(phenotype_id)
        
        nodes = []
        nodes.append(create_node(id_to_biocon[phenotype_id], True))
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in grandchildren if x.child_id in viable_ids and x.parent_id in viable_ids])
    
    return {'nodes': list(nodes), 'edges': edges}
        