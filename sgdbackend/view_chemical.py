'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.chemical import Chemicalrelation
from sgdbackend_query.query_misc import get_relations
from sgdbackend_utils.cache import id_to_chem

'''
-------------------------------Ontology Graph---------------------------------------
''' 

def create_node(biocon, is_focus, is_child, is_parent):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(biocon['id']), 'name':biocon['display_name'], 'link': biocon['link'], 
                    'is_child': is_child, 'is_parent': is_parent, 'sub_type':sub_type}}

def create_edge(interaction_id, biocon1_id, biocon2_id):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id)}} 

def make_ontology_graph(phenotype_id):
    children = get_relations(Chemicalrelation, None, parent_ids=[phenotype_id])    
    parents = get_relations(Chemicalrelation, None, child_ids=[phenotype_id])
    if len(parents) > 0:
        grandparents = get_relations(Chemicalrelation, None, child_ids=[parent.parent_id for parent in parents])
        greatgrandparents = get_relations(Chemicalrelation, None, child_ids=[parent.parent_id for parent in grandparents])
        greatgreatgrandparents = get_relations(Chemicalrelation, None, child_ids=[parent.parent_id for parent in greatgrandparents])
        nodes = []
        nodes.append(create_node(id_to_chem[phenotype_id], True, True, True))
        
        child_ids = set([x.child_id for x in children])
        parent_ids = set([x.parent_id for x in parents])
        parent_ids.update([x.parent_id for x in grandparents])
        parent_ids.update([x.parent_id for x in greatgrandparents])
        parent_ids.update([x.parent_id for x in greatgreatgrandparents])
        
        nodes.extend([create_node(id_to_chem[x], False, True, False) for x in child_ids])
        nodes.extend([create_node(id_to_chem[x], False, False, True) for x in parent_ids])
        
        edges = []
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in children])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in parents])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in grandparents])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in greatgrandparents])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in greatgreatgrandparents])
    else:
        grandchildren = get_relations(Chemicalrelation, None, parent_ids=[x.child_id for x in children])  
        
        child_ids = set([x.child_id for x in children])
        child_ids.update([x.child_id for x in grandchildren])  
        
        nodes = []
        nodes.append(create_node(id_to_chem[phenotype_id], True, True, True))
        nodes.extend([create_node(id_to_chem[x], False, True, False) for x in child_ids])
        
        edges = []
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in children])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in grandchildren])
    
    return {'nodes': list(nodes), 'edges': edges}

