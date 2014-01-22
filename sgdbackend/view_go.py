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
from sgdbackend_query.query_paragraph import get_paragraph
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
    goevidences = get_evidence(Goevidence, bioent_id=bioent_id)

    if goevidences is None:
        return {'biological process': {'Error': 'Too much data to display.'}, 'molecular function':{'Error': 'Too much data to display.'}, 'cellular component':{'Error': 'Too much data to display.'}}

    comp_mutant_to_phenotypes = {'biological process':set(), 'molecular function':set(), 'cellular component':set()}
    htp_to_phenotypes = {'biological process':set(), 'molecular function':set(), 'cellular component':set()}
    manual_to_phenotypes = {'biological process':set(), 'molecular function':set(), 'cellular component':set()}

    for goevidence in goevidences:
        bioconcept = id_to_biocon[goevidence.bioconcept_id]
        aspect = bioconcept['go_aspect']
        if goevidence.annotation_type == 'computational':
            comp_mutant_to_phenotypes[aspect].add(goevidence.bioconcept_id)
        elif goevidence.annotation_type == 'high-throughput':
            htp_to_phenotypes[aspect].add(goevidence.bioconcept_id)
        elif goevidence.annotation_type == 'manually curated':
            manual_to_phenotypes[aspect].add(goevidence.bioconcept_id)

    aspect_to_count = dict([(x, (0 if x not in manual_to_phenotypes else len(manual_to_phenotypes[x]),
                                 0 if x not in htp_to_phenotypes else len(htp_to_phenotypes[x]),
                                 0 if x not in comp_mutant_to_phenotypes else len(comp_mutant_to_phenotypes[x]))) for x in ['biological process', 'molecular function', 'cellular component']])

    overview = {'annotation_types': ['manually curated', 'high-throughput', 'computational'], 'aspect_to_count': aspect_to_count, 'aspects': ['biological process', 'molecular function', 'cellular component']}

    paragraph = get_paragraph(bioent_id, 'GO')
    if paragraph is not None:
        overview['date_last_reviewed'] = paragraph.text

    return overview


    
'''
-------------------------------Details---------------------------------------
'''
    
def make_details(locus_id=None, go_id=None, chemical_id=None, reference_id=None, with_children=False):
    goevidences = get_evidence(Goevidence, bioent_id=locus_id, biocon_id=go_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)
    
    id_to_conditions = {}
    for condition in get_conditions([x.id for x in goevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]
    
    if locus_id is not None or chemical_id is not None:  
        bp_evidence = [x for x in goevidences if id_to_biocon[x.bioconcept_id]['go_aspect'] == 'biological process']      
        mf_evidence = [x for x in goevidences if id_to_biocon[x.bioconcept_id]['go_aspect'] == 'molecular function']    
        cc_evidence = [x for x in goevidences if id_to_biocon[x.bioconcept_id]['go_aspect'] == 'cellular component']
    
        tables = {}
        tables['biological_process'] = create_simple_table(bp_evidence, make_evidence_row, id_to_conditions=id_to_conditions)
        tables['molecular_function'] = create_simple_table(mf_evidence, make_evidence_row, id_to_conditions=id_to_conditions)
        tables['cellular_component'] = create_simple_table(cc_evidence, make_evidence_row, id_to_conditions=id_to_conditions)
    else:
        tables = create_simple_table(goevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        
    return tables  

def make_evidence_row(goevidence, id_to_conditions): 
    bioentity_id = goevidence.bioentity_id
    bioconcept_id = goevidence.bioconcept_id
    #with_conditions = [] if goevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[goevidence.id] if x.role == 'With']
    #from_conditions = [] if goevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[goevidence.id] if x.role == 'From']
        
    obj_json = evidence_to_json(goevidence).copy()
    obj_json['bioentity'] = minimize_json(id_to_bioent[bioentity_id], include_format_name=True)
    obj_json['bioconcept'] = minimize_json(id_to_biocon[bioconcept_id])
    #obj_json['with'] = with_conditions
    #obj_json['from']= from_conditions
    obj_json['conditions'] = [] if goevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[goevidence.id]]
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

def create_edge(biocon1_id, biocon2_id, label):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id), 'name':None if label == 'is a' else label}}

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

        relations = set()
        relations.update(children)
        relations.update(parents)
        relations.update(grandparents)
        relations.update(greatgrandparents)
        relations.update(greatgreatgrandparents)
        edges = [create_edge(x.child_id, x.parent_id, x.relation_type) for x in relations if x.child_id in viable_ids and x.parent_id in viable_ids]

    else:
        #grandchildren = get_relations(Bioconceptrelation, 'GO', parent_ids=[x.child_id for x in children])
        
        child_ids = set([x.child_id for x in children])
        #child_ids.update([x.child_id for x in grandchildren])
        
        child_id_to_child = dict([(x, id_to_biocon[x]) for x in child_ids])
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['child_count'] > 0])
        viable_ids.add(phenotype_id)
        
        nodes = []
        nodes.append(create_node(id_to_biocon[phenotype_id], True))
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])

        relations = set()
        relations.update(children)
        #relations.update(grandchildren)
        edges = [create_edge(x.child_id, x.parent_id, x.relation_type) for x in relations if x.child_id in viable_ids and x.parent_id in viable_ids]

    return {'nodes': list(nodes), 'edges': edges}

'''
-------------------------------Snapshot---------------------------------------
'''
def make_snapshot():
    snapshot = {}
    return snapshot