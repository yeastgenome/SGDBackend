from src.sgd.model.nex.bioentity import Protein
from src.sgd.model.nex.bioitem import Domain
from src.sgd.model.nex.evidence import Domainevidence, Phosphorylationevidence, Proteinexperimentevidence
from src.sgd.backend.nex import DBSession, query_limit

__author__ = 'kpaskov'

# -------------------------------Overview---------------------------------------
def make_overview(locus_id):
    proteins = DBSession.query(Protein).filter_by(locus_id=locus_id).all()
    return [x.to_json() for x in proteins]

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

    domain_evidences = [x for x in domain_evidences if x.bioitem.display_name != 'seg']

    return [x.to_json() for x in domain_evidences]

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

    return [x.to_json() for x in sorted(phospho_evidences, key=lambda x: x.site_index)]

# -------------------------------Details---------------------------------------
def get_protein_experiment_evidence(protein_id):
    query = DBSession.query(Proteinexperimentevidence)
    if protein_id is not None:
        query = query.filter_by(bioentity_id=protein_id)

    if query.count() > query_limit:
        return None
    return query.all()

def get_protein_experiment_evidence_for_locus(locus_id):
    evidences = []
    protein_ids = [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for protein_id in protein_ids:
        more_evidences = get_protein_experiment_evidence(protein_id=protein_id)
        if more_evidences is None or len(evidences) + len(more_evidences) > query_limit:
            return None
        evidences.extend(more_evidences)
    return evidences

def make_protein_experiment_details(locus_id=None, protein_id=None):
    if locus_id is None and protein_id is None:
        return {'Error': 'No locus_id or protein_id given.'}

    if protein_id is not None:
        evidences = get_protein_experiment_evidence(protein_id=None)
    else:
        evidences = get_protein_experiment_evidence_for_locus(locus_id=locus_id)

    return [x.to_json() for x in evidences]

# -------------------------------Graph-----------------------------------------
def create_bioent_node(bioent, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BioentNode' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link,
                    'sub_type':sub_type, 'type': 'BIOENTITY'}}

def create_domain_node(bioitem):
    return {'data':{'id':'DomainNode' + str(bioitem.id), 'name':bioitem.display_name, 'link': bioitem.link,
                    'sub_type':bioitem.source.display_name, 'type': 'BIOITEM', 'source': bioitem.source.display_name}}

def create_edge(bioent_id, domain_id):
    return {'data':{'target': 'BioentNode' + str(bioent_id), 'source': 'DomainNode' + str(domain_id)}}

def make_graph(locus_id):
    domain_ids = set()
    protein_ids = [x.id for x in DBSession.query(Protein).filter_by(locus_id=locus_id).all()]
    for pid in protein_ids:
        domain_ids.update([x.bioitem_id for x in get_protein_domain_evidence(protein_id=pid, domain_id=None) if x.bioitem.display_name != 'seg'])

    domain_id_to_bioent_ids = {}
    bioent_id_to_domain_ids = {}

    all_relevant_edges = set()
    for domain_id in domain_ids:
        domain_domainevidences = get_protein_domain_evidence(protein_id=None, domain_id=domain_id)
        all_relevant_edges.update([(x.bioentity_id, x.bioitem_id) for x in domain_domainevidences if x.bioitem.display_name != 'seg'])

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

        nodes = [create_bioent_node(x, x.id in protein_ids) for x in DBSession.query(Protein).filter(Protein.id.in_(bioent_ids_in_use)).all()]
        nodes.extend([create_domain_node(x) for x in DBSession.query(Domain).filter(Domain.id.in_(domain_ids_in_use)).all()])

        edges = [create_edge(evidence[0], evidence[1]) for evidence in edges_in_use]

        return {'nodes': nodes, 'edges': edges, 'max_cutoff': max(bioent_to_score.values()), 'min_cutoff':cutoff if len(bioent_ids_in_use) == 1 else min([bioent_to_score[x] for x in bioent_ids_in_use if x not in protein_ids])}
    else:
        return {'nodes':[], 'edges':[], 'max_cutoff':0, 'min_cutoff':0}