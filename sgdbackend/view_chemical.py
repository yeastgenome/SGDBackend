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

def create_node(biocon, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(biocon['id']), 'name':biocon['display_name'], 'link': biocon['link'], 
                    'sub_type':sub_type}}

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
        nodes.append(create_node(id_to_chem[phenotype_id], True))
        
        child_ids = set([x.child_id for x in children])
        parent_ids = set([x.parent_id for x in parents])
        parent_ids.update([x.parent_id for x in grandparents])
        parent_ids.update([x.parent_id for x in greatgrandparents])
        parent_ids.update([x.parent_id for x in greatgreatgrandparents])
        
        child_id_to_child = dict([(x, id_to_chem[x]) for x in child_ids])
        parent_id_to_parent = dict([(x, id_to_chem[x]) for x in parent_ids])
        viable_ids = set([k for k, v in child_id_to_child.iteritems()])
        viable_ids.update([k for k, v in parent_id_to_parent.iteritems()])
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
        grandchildren = get_relations(Chemicalrelation, None, parent_ids=[x.child_id for x in children])  
        
        child_ids = set([x.child_id for x in children])
        child_ids.update([x.child_id for x in grandchildren])  
        
        child_id_to_child = dict([(x, id_to_chem[x]) for x in child_ids])
        viable_ids = set([k for k, v in child_id_to_child.iteritems()])
        viable_ids.add(phenotype_id)
        
        nodes = []
        nodes.append(create_node(id_to_chem[phenotype_id], True))
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in grandchildren if x.child_id in viable_ids and x.parent_id in viable_ids])
    
    return {'nodes': list(nodes), 'edges': edges}

