'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconceptrelation, Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import ECNumberevidence
from sgdbackend_query import get_evidence
from sgdbackend_query.query_misc import get_relations
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import get_obj, get_objs
from sgdbackend_utils.obj_to_json import minimize_json, \
    evidence_to_json

# -------------------------------Details---------------------------------------
    
def make_details(locus_id=None, ec_number_id=None, with_children=False):

    ecevidences = get_evidence(ECNumberevidence, bioent_id=locus_id, biocon_id=ec_number_id, with_children=with_children)
    if ecevidences is None:
        return {'Error': 'Too much data to display.'}
            
    tables = create_simple_table(ecevidences, make_evidence_row)
    return tables  

def make_evidence_row(ecevidence):
    bioentity_id = ecevidence.bioentity_id
    bioconcept_id = ecevidence.bioconcept_id
        
    obj_json = evidence_to_json(ecevidence).copy()
    obj_json['bioentity'] = minimize_json(get_obj(Bioentity, bioentity_id), include_format_name=True)
    obj_json['bioconcept'] = minimize_json(get_obj(Bioconcept, bioconcept_id))
    return obj_json

# -------------------------------Ontology Graph---------------------------------------

def create_node(biocon, is_focus):
    if is_focus:
        sub_type = 'FOCUS'
    else:
        sub_type = biocon['ancestor_type']
    return {'data':{'id':'Node' + str(biocon['id']), 'name':biocon['display_name'] + ('' if biocon['format_name'] == 'ypo' else ' (' + str(biocon['count']) + ')'), 'link': biocon['link'],
                    'sub_type':sub_type}}

def create_ontology_edge(interaction_id, biocon1_id, biocon2_id):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id)}} 

def make_ontology_graph(phenotype_id):
    all_children = None
    children = get_relations(Bioconceptrelation, 'EC_NUMBER', parent_ids=[phenotype_id])
    parents = get_relations(Bioconceptrelation, 'EC_NUMBER', child_ids=[phenotype_id])
    if len(parents) > 0:
        grandparents = get_relations(Bioconceptrelation, 'EC_NUMBER', child_ids=[parent.parent_id for parent in parents])
        great_grandparents = get_relations(Bioconceptrelation, 'EC_NUMBER', child_ids=[parent.parent_id for parent in grandparents])
        great_great_grandparents = get_relations(Bioconceptrelation, 'EC_NUMBER', child_ids=[parent.parent_id for parent in great_grandparents])
        nodes = []
        nodes.append(create_node(get_obj(Bioconcept, phenotype_id), True))
        
        child_ids = set([x.child_id for x in children])
        parent_ids = set([x.parent_id for x in parents])
        parent_ids.update([x.parent_id for x in grandparents])
        parent_ids.update([x.parent_id for x in great_grandparents])
        parent_ids.update([x.parent_id for x in great_great_grandparents])
        
        child_id_to_child = get_objs(Bioconcept, child_ids)
        parent_id_to_parent = get_objs(Bioconcept, parent_ids)
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['is_core']])

        #If there are too many children, hide some.
        all_children = []
        hidden_children_count = 0
        if len(viable_ids) > 8:
            all_children = sorted(get_objs(Bioconcept, viable_ids).values(), key=lambda x: x['display_name'])
            hidden_children_count = len(viable_ids)-7
            viable_ids = set(list(viable_ids)[:7])

        viable_ids.update([k for k, v in parent_id_to_parent.iteritems() if v['is_core']])
        viable_ids.add(phenotype_id)
        
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        nodes.extend([create_node(v, False) for k, v in parent_id_to_parent.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in parents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in great_grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in great_great_grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])

        if hidden_children_count > 0:
            nodes.insert(0, {'data':{'id':'NodeMoreChildren', 'name':str(hidden_children_count) + ' more children', 'link': None, 'sub_type':get_obj(Bioconcept, phenotype_id)['ancestor_type']}})
            edges.insert(0, {'data':{'target': 'NodeMoreChildren', 'source': 'Node' + str(phenotype_id)}})

    else:
        grandchildren = get_relations(Bioconceptrelation, 'EC_NUMBER', parent_ids=[x.child_id for x in children])
        
        child_ids = set([x.child_id for x in children])
        child_ids.update([x.child_id for x in grandchildren])  
        
        child_id_to_child = get_objs(Bioconcept, child_ids)
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['is_core']])
        viable_ids.add(phenotype_id)
        
        nodes = []
        nodes.append(create_node(get_obj(Bioconcept, phenotype_id), True))
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in grandchildren if x.child_id in viable_ids and x.parent_id in viable_ids])
    
    return {'nodes': list(nodes), 'edges': edges, 'all_children': all_children}