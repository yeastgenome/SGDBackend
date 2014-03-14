from src.sgd.model.nex.bioentity import Bioentity, Protein
from src.sgd.model.nex.bioitem import Bioitem
from src.sgd.model.nex.evidence import Domainevidence, Phosphorylationevidence
from src.sgd.backend.nex import DBSession, create_simple_table, query_limit
from src.sgd.backend.nex.cache import get_obj
from src.sgd.backend.nex.obj_to_json import evidence_to_json

__author__ = 'kpaskov'

# -------------------------------Overview---------------------------------------
def make_overview(locus_id):
    proteins = []
    protein_ids = [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for protein_id in protein_ids:
        proteins.append(get_obj(Bioentity, protein_id))
    return proteins

# -------------------------------Details---------------------------------------
def get_protein_domain_evidence(protein_id, domain_id):
    query = DBSession.query(Domainevidence)
    if protein_id is not None:
        query = query.filter_by(bioentity_id=protein_id)
    if domain_id is not None:
        query = query.filter_by(bioitem_id=domain_id)

    if query.count() > query_limit:
        return None
    return query.all()

def get_protein_domain_evidence_for_locus(locus_id, domain_id):
    domainevidences = []
    protein_ids = [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for protein_id in protein_ids:
        more_evidences = get_protein_domain_evidence(protein_id=protein_id, domain_id=domain_id)
        if more_evidences is None or len(domainevidences) + len(more_evidences) > query_limit:
            return None
        domainevidences.extend(more_evidences)
    return domainevidences

def make_details(locus_id=None, protein_id=None, domain_id=None):
    if locus_id is None and protein_id is None and domain_id is None:
        return {'Error': 'No locus_id or protein_id or domain_id given.'}

    if protein_id is not None:
        domain_evidences = get_protein_domain_evidence(protein_id=protein_id, domain_id=domain_id)
    elif locus_id is not None:
        domain_evidences = get_protein_domain_evidence_for_locus(locus_id=locus_id, domain_id=domain_id)
    else:
        domain_evidences = get_protein_domain_evidence(protein_id=None, domain_id=domain_id)

    if domain_evidences is None:
        return {'Error': 'Too much data to display.'}

    domain_evidences = [x for x in domain_evidences if get_obj(Bioitem, x.bioitem_id)['display_name'] != 'seg']

    return create_simple_table(domain_evidences, make_evidence_row) 

def make_evidence_row(domain_evidence): 
    obj_json = evidence_to_json(domain_evidence).copy()
    obj_json['protein'] = get_obj(Bioentity, domain_evidence.bioentity_id)
    obj_json['domain'] = get_obj(Bioitem, domain_evidence.bioitem_id)
    obj_json['start'] = domain_evidence.start
    obj_json['end'] = domain_evidence.end
    obj_json['evalue'] = domain_evidence.evalue
    obj_json['status'] = domain_evidence.status
    obj_json['date_of_run'] = domain_evidence.date_of_run
    obj_json['domain']['count'] = len(set([x.bioentity_id for x in get_protein_domain_evidence(protein_id=None, domain_id=domain_evidence.bioitem_id)]))
    return obj_json

# -------------------------------Details---------------------------------------
def get_phosphorylation_evidence(protein_id):
    query = DBSession.query(Phosphorylationevidence)
    if protein_id is not None:
        query = query.filter_by(bioentity_id=protein_id)

    if query.count() > query_limit:
        return None
    return query.all()

def get_phosphorylation_evidence_for_locus(locus_id):
    phosphoevidences = []
    protein_ids = [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for protein_id in protein_ids:
        more_evidences = get_phosphorylation_evidence(protein_id=protein_id)
        if more_evidences is None or len(phosphoevidences) + len(more_evidences) > query_limit:
            return None
        phosphoevidences.extend(more_evidences)
    return phosphoevidences

def make_phosphorylation_details(locus_id=None, protein_id=None):
    if locus_id is None and protein_id is None:
        return {'Error': 'No locus_id or protein_id given.'}

    if protein_id is not None:
        phospho_evidences = get_phosphorylation_evidence(protein_id=None)
    else:
        phospho_evidences = get_phosphorylation_evidence_for_locus(locus_id=locus_id)

    return create_simple_table(sorted(phospho_evidences, key=lambda x: x.site_index), make_phospho_evidence_row)

def make_phospho_evidence_row(phospho_evidence):
    obj_json = evidence_to_json(phospho_evidence).copy()
    obj_json['protein'] = get_obj(Bioentity, phospho_evidence.bioentity_id)
    obj_json['site_index'] = phospho_evidence.site_index
    obj_json['site_residue'] = phospho_evidence.site_residue
    return obj_json

# -------------------------------Graph-----------------------------------------
def create_bioent_node(bioent, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BioentNode' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'],
                    'sub_type':sub_type, 'type': 'BIOENTITY'}}

def create_domain_node(bioitem):
    return {'data':{'id':'DomainNode' + str(bioitem['id']), 'name':bioitem['display_name'], 'link': bioitem['link'],
                    'sub_type':None, 'type': 'BIOITEM', 'source': bioitem['source']}}

def create_edge(bioent_id, domain_id):
    return {'data':{'target': 'BioentNode' + str(bioent_id), 'source': 'DomainNode' + str(domain_id)}}

def make_graph(locus_id):
    domain_ids = set()
    protein_ids = [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for pid in protein_ids:
        domain_ids.update([x.bioitem_id for x in get_protein_domain_evidence(protein_id=pid, domain_id=None) if x.domain.display_name != 'seg'])

    domain_id_to_bioent_ids = {}
    bioent_id_to_domain_ids = {}

    all_relevant_edges = set()
    for domain_id in domain_ids:
        domain_domainevidences = get_protein_domain_evidence(protein_id=None, domain_id=domain_id)
        all_relevant_edges.update([(x.bioentity_id, x.bioitem_id) for x in domain_domainevidences if x.domain.display_name != 'seg'])

    for edge in all_relevant_edges:
        bioentity_id = edge[0]
        domain_id = edge[1]

        if domain_id in domain_id_to_bioent_ids:
            domain_id_to_bioent_ids[domain_id].add(bioentity_id)
        else:
            domain_id_to_bioent_ids[domain_id] = {bioentity_id}

        if bioentity_id in bioent_id_to_domain_ids:
            bioent_id_to_domain_ids[bioentity_id].add(domain_id)
        else:
            bioent_id_to_domain_ids[bioentity_id] = {domain_id}

    cutoff = 1
    node_count = len(bioent_id_to_domain_ids) + len(domain_id_to_bioent_ids)
    edge_count = len(all_relevant_edges)
    bioent_count = len(bioent_id_to_domain_ids)
    domain_ids_in_use = set([x for x, y in domain_id_to_bioent_ids.iteritems()])
    bioent_ids_in_use = set([x for x, y in bioent_id_to_domain_ids.iteritems()])
    edges_in_use = [x for x in all_relevant_edges]
    while node_count > 100 or edge_count > 250 or bioent_count > 50:
        cutoff = cutoff + 1
        bioent_ids_in_use = set([x for x, y in bioent_id_to_domain_ids.iteritems() if len(y) >= cutoff])
        domain_ids_in_use = set([x for x, y in domain_id_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
        edges_in_use = [x for x in all_relevant_edges if x[0] in bioent_ids_in_use and x[1] in domain_ids_in_use]
        node_count = len(bioent_ids_in_use) + len(domain_ids_in_use)
        edge_count = len(edges_in_use)
        bioent_count = len(bioent_ids_in_use)

    if len(bioent_ids_in_use) > 0:

        bioent_to_score = dict({(x, len(y&domain_ids_in_use)) for x, y in bioent_id_to_domain_ids.iteritems()})
        nodes = []
        for pid in protein_ids:
            bioent_to_score[pid] = 0

        nodes = [create_bioent_node(get_obj(Bioentity, x), x in protein_ids) for x in bioent_ids_in_use]
        nodes.extend([create_domain_node(get_obj(Bioitem, x)) for x in domain_ids_in_use])

        edges = [create_edge(evidence[0], evidence[1]) for evidence in edges_in_use]

        return {'nodes': nodes, 'edges': edges, 'max_cutoff': max(bioent_to_score.values()), 'min_cutoff':cutoff if len(bioent_ids_in_use) == 1 else min([bioent_to_score[x] for x in bioent_ids_in_use if x not in protein_ids])}
    else:
        return {'nodes':[], 'edges':[], 'max_cutoff':0, 'min_cutoff':0}