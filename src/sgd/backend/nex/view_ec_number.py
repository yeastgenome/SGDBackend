from math import ceil

from src.sgd.backend.nex import create_simple_table, DBSession, query_limit
from src.sgd.backend.nex.query_tools import get_all_bioconcept_children, get_relations
from src.sgd.model.nex.bioconcept import Bioconceptrelation, Bioconcept
from src.sgd.model.nex.bioentity import Bioentity, Protein
from src.sgd.model.nex.evidence import ECNumberevidence
from src.sgd.backend.nex.cache import get_obj, get_objs
from src.sgd.backend.nex.obj_to_json import minimize_json, \
    evidence_to_json


__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_ec_number_evidence(protein_id, ec_number_id, with_children):
    query = DBSession.query(ECNumberevidence)
    if protein_id is not None:
        query = query.filter_by(bioentity_id=protein_id)
    if ec_number_id is not None:
        if with_children:
            child_ids = list(get_all_bioconcept_children(ec_number_id))
            num_chunks = int(ceil(1.0*len(child_ids)/500))
            evidences = []
            for i in range(num_chunks):
                subquery = query.filter(ECNumberevidence.bioconcept_id.in_(child_ids[i*500:(i+1)*500]))
                if len(evidences) + subquery.count() > query_limit:
                    return None
                evidences.extend([x for x in subquery.all()])
            return evidences
        else:
            query = query.filter_by(bioconcept_id=ec_number_id)

    if query.count() > query_limit:
        return None
    return query.all()

def get_ec_number_evidence_for_locus(locus_id, ec_number_id, with_children):
    ecevidences = []
    protein_ids = [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for protein_id in protein_ids:
        more_evidences = get_ec_number_evidence(protein_id=protein_id, ec_number_id=ec_number_id, with_children=with_children)
        if more_evidences is None or len(ecevidences) + len(more_evidences) > query_limit:
            return None
        ecevidences.extend(more_evidences)
    return ecevidences

def make_details(locus_id=None, protein_id=None, ec_number_id=None, with_children=False):
    if locus_id is None and ec_number_id is None:
        return {'Error': 'No locus_id or ec_number_id given.'}

    if protein_id is not None:
        ecevidences = get_ec_number_evidence(protein_id=protein_id, ec_number_id=ec_number_id, with_children=with_children)
    elif locus_id is not None:
        ecevidences = get_ec_number_evidence_for_locus(locus_id=locus_id, ec_number_id=ec_number_id, with_children=with_children)
    else:
        ecevidences = get_ec_number_evidence(protein_id=None, ec_number_id=ec_number_id, with_children=with_children)

    if ecevidences is None:
        return {'Error': 'Too much data to display.'}
            
    tables = create_simple_table(ecevidences, make_evidence_row)
    return tables  

def make_evidence_row(ecevidence):
    bioentity_id = ecevidence.bioentity_id
    bioconcept_id = ecevidence.bioconcept_id
        
    obj_json = evidence_to_json(ecevidence).copy()
    obj_json['bioentity'] = get_obj(Bioentity, bioentity_id)
    obj_json['bioentity']['locus']['description'] = get_obj(Bioentity, obj_json['bioentity']['locus']['id'])['description']
    obj_json['bioconcept'] = minimize_json(get_obj(Bioconcept, bioconcept_id))
    return obj_json

# -------------------------------Ontology Graph---------------------------------------
def create_node(biocon, is_focus):
    return {'data':{'id':'Node' + str(biocon['id']), 'name':biocon['display_name'] + ('' if biocon['format_name'] == 'ypo' else ' (' + str(biocon['count']) + ')'), 'link': biocon['link'],
                    'sub_type':'FOCUS' if is_focus else None}}

def create_ontology_edge(interaction_id, biocon1_id, biocon2_id):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id)}} 

def make_ontology_graph(ec_number_id):
    all_children = None
    children = get_relations(Bioconceptrelation, 'EC_NUMBER', parent_ids=[ec_number_id])
    parents = get_relations(Bioconceptrelation, 'EC_NUMBER', child_ids=[ec_number_id])
    if len(parents) > 0:
        grandparents = get_relations(Bioconceptrelation, 'EC_NUMBER', child_ids=[parent.parent_id for parent in parents])
        great_grandparents = get_relations(Bioconceptrelation, 'EC_NUMBER', child_ids=[parent.parent_id for parent in grandparents])
        great_great_grandparents = get_relations(Bioconceptrelation, 'EC_NUMBER', child_ids=[parent.parent_id for parent in great_grandparents])
        nodes = []
        nodes.append(create_node(get_obj(Bioconcept, ec_number_id), True))
        
        child_ids = set([x.child_id for x in children])
        parent_ids = set([x.parent_id for x in parents])
        parent_ids.update([x.parent_id for x in grandparents])
        parent_ids.update([x.parent_id for x in great_grandparents])
        parent_ids.update([x.parent_id for x in great_great_grandparents])
        
        child_id_to_child = get_objs(Bioconcept, child_ids)
        parent_id_to_parent = get_objs(Bioconcept, parent_ids)
        viable_ids = set([k for k, v in child_id_to_child.iteritems()])

        #If there are too many children, hide some.
        all_children = []
        hidden_children_count = 0
        if len(viable_ids) > 8:
            all_children = sorted(get_objs(Bioconcept, viable_ids).values(), key=lambda x: x['display_name'])
            hidden_children_count = len(viable_ids)-7
            viable_ids = set(list(viable_ids)[:7])

        viable_ids.update([k for k, v in parent_id_to_parent.iteritems()])
        viable_ids.add(ec_number_id)
        
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        nodes.extend([create_node(v, False) for k, v in parent_id_to_parent.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in parents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in great_grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in great_great_grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])

        if hidden_children_count > 0:
            nodes.insert(0, {'data':{'id':'NodeMoreChildren', 'name':str(hidden_children_count) + ' more children', 'link': None, 'sub_type':None}})
            edges.insert(0, {'data':{'target': 'NodeMoreChildren', 'source': 'Node' + str(ec_number_id)}})

    else:
        grandchildren = get_relations(Bioconceptrelation, 'EC_NUMBER', parent_ids=[x.child_id for x in children])
        
        child_ids = set([x.child_id for x in children])
        child_ids.update([x.child_id for x in grandchildren])  
        
        child_id_to_child = get_objs(Bioconcept, child_ids)
        viable_ids = set([k for k, v in child_id_to_child.iteritems()])
        viable_ids.add(ec_number_id)
        
        nodes = []
        nodes.append(create_node(get_obj(Bioconcept, ec_number_id), True))
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in grandchildren if x.child_id in viable_ids and x.parent_id in viable_ids])
    
    return {'nodes': list(nodes), 'edges': edges, 'all_children': all_children}