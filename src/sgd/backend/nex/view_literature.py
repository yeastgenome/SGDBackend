from sqlalchemy import func

from src.sgd.model.nex.evidence import Literatureevidence, Goevidence, Regulationevidence, Phenotypeevidence, \
    Physinteractionevidence, Geninteractionevidence
from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.model.nex.archive import ArchiveLiteratureevidence
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.auxiliary import Referenceinteraction


__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_literature_evidence(locus_id, reference_id, topic):
    query = DBSession.query(Literatureevidence)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)
    if topic is not None:
        query = query.filter(func.lower(Literatureevidence.topic) == topic.lower())

    if query.count() > query_limit:
        return None
    return query.all()

def get_archived_literature_evidence(locus_id, reference_id, topic):
    query = DBSession.query(ArchiveLiteratureevidence)
    if locus_id is not None:
        query = query.filter_by(bioentity_id=locus_id)
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)
    if topic is not None:
        query = query.filter(func.lower(ArchiveLiteratureevidence.topic) == topic.lower())

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, reference_id=None, topic=None):
    if locus_id is None and reference_id is None and topic is None:
        return {'Error': 'No locus_id or reference_id or topic given.'}

    evidences = get_literature_evidence(locus_id=locus_id, reference_id=reference_id, topic=topic)

    if evidences is None:
        return {'Error': 'Too much data to display.'}

    if locus_id is not None:
        evidences.extend(dict([(x.reference_id, Literatureevidence({'reference': x.reference, 'locus': x.locus, 'topic': 'GO', 'source_id': 1})) for x in DBSession.query(Goevidence).filter_by(locus_id=locus_id).all()]).values())
        evidences.extend(dict([(x.reference_id, Literatureevidence({'reference': x.reference, 'locus': x.locus, 'topic': 'Phenotype', 'source_id': 1})) for x in DBSession.query(Phenotypeevidence).filter_by(locus_id=locus_id).all()]).values())

        regulation_evidences = dict([(x.reference_id, Literatureevidence({'reference': x.reference, 'locus': x.locus1, 'topic': 'Regulation', 'source_id': 1})) for x in DBSession.query(Regulationevidence).filter_by(locus1_id=locus_id).all()])
        regulation_evidences.update([(x.reference_id, Literatureevidence({'reference': x.reference, 'locus': x.locus2, 'topic': 'Regulation', 'source_id': 1})) for x in DBSession.query(Regulationevidence).filter_by(locus2_id=locus_id).all()])
        evidences.extend(regulation_evidences.values())

        interaction_evidences = dict([(x.reference_id, Literatureevidence({'reference': x.reference, 'locus': x.locus1, 'topic': 'Interaction', 'source_id': 1})) for x in DBSession.query(Physinteractionevidence).filter_by(locus1_id=locus_id).all()])
        interaction_evidences.update([(x.reference_id, Literatureevidence({'reference': x.reference, 'locus': x.locus2, 'topic': 'Interaction', 'source_id': 1})) for x in DBSession.query(Physinteractionevidence).filter_by(locus2_id=locus_id).all()])
        interaction_evidences.update([(x.reference_id, Literatureevidence({'reference': x.reference, 'locus': x.locus1, 'topic': 'Interaction', 'source_id': 1})) for x in DBSession.query(Geninteractionevidence).filter_by(locus1_id=locus_id).all()])
        interaction_evidences.update([(x.reference_id, Literatureevidence({'reference': x.reference, 'locus': x.locus2, 'topic': 'Interaction', 'source_id': 1})) for x in DBSession.query(Geninteractionevidence).filter_by(locus2_id=locus_id).all()])
        evidences.extend(interaction_evidences.values())
        return [x.to_json() for x in sorted(evidences, key=lambda x: (x.reference.year, x.reference.pubmed_id), reverse=True)]
    elif reference_id is not None:
        return [x.to_json() for x in sorted(evidences, key=lambda x: x.locus.display_name)]
    return [x.to_json() for x in evidences]

# -------------------------------Graph---------------------------------------
def create_litguide_bioent_node(bioent, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'LocusNode' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link,
                    'sub_type':sub_type, 'type': 'BIOENT'}}
    
def create_litguide_ref_node(reference, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'RefNode' + str(reference.id), 'name':reference.display_name, 'link': reference.link,
                    'sub_type':sub_type, 'type': 'REFERENCE'}}

def create_litguide_edge(bioent_id, reference_id):
    return {'data':{'target': 'LocusNode' + str(bioent_id), 'source': 'RefNode' + str(reference_id)}}

def make_graph(bioent_id):
    
    #Get primary genes for each paper in bioentevidences
    reference_ids = [x.reference_id for x in DBSession.query(Referenceinteraction).filter_by(interaction_type='PRIMARY_LITERATURE').filter_by(locus_id==bioent_id).all()]

    reference_id_to_bioent_ids = {}
    for bioent_ref in DBSession.query(Referenceinteraction).filter_by(interaction_type='PRIMARY_LITERATURE').filter(reference_id.in_(reference_ids)).all():
        bioentity_id = bioent_ref.bioentity_id
        reference_id = bioent_ref.interator_id
        if reference_id in reference_id_to_bioent_ids:
            reference_id_to_bioent_ids[reference_id].add(bioentity_id)
        else:
            reference_id_to_bioent_ids[reference_id] = {bioentity_id}
     
    #Calculate weight between every pair of papers
    reference_pair_to_weight = {}
    for reference_id1 in reference_ids:
        for reference_id2 in reference_ids:
            if reference_id1 < reference_id2:
                bioent_ids1 = reference_id_to_bioent_ids[reference_id1]
                bioent_ids2 = reference_id_to_bioent_ids[reference_id2]
                overlap = bioent_ids1 & bioent_ids2
                overlap_len = len(overlap)
                if overlap_len > 1 and len(bioent_ids2) <= 10 and len(bioent_ids2) <= 10:
                    weight = 1.0*overlap_len*overlap_len*overlap_len/(len(bioent_ids1)*len(bioent_ids2))
                    reference_pair_to_weight[reference_id1, reference_id2] = weight
                
    #Find papers with top 20 weights.
    max_num = 15
    top_ref_pairs = []

    for ref_pair, weight in reference_pair_to_weight.iteritems():
        if len(top_ref_pairs) < max_num:
            top_ref_pairs.append((ref_pair, weight))
        elif weight > top_ref_pairs[0][1]:
            top_ref_pairs.pop()
            top_ref_pairs.append((ref_pair, weight))
        top_ref_pairs.sort(key=lambda k:k[1])
    
    top_references = set()
    for pair in top_ref_pairs:
        ref1, ref2 = pair[0]
        top_references.add(ref1)
        top_references.add(ref2)
    
    nodes = {}
    nodes_ive_seen = set()
    for reference in DBSession.query(Reference).filter(Reference.id.in_(top_references)).all():
        reference_id = reference.id
        nodes['Ref' + str(reference_id)] = create_litguide_ref_node(reference, False)
        for neigh in DBSession.query(Bioentity).filter(Bioentity.id.in_(reference_id_to_bioent_ids[reference_id])).all():
            neigh_id = neigh.id
            if neigh_id in nodes_ive_seen:
                nodes[neigh_id] = create_litguide_bioent_node(neigh, False)
            else:
                nodes_ive_seen.add(neigh_id)
    nodes[bioent_id] = create_litguide_bioent_node(DBSession.query(Bioentity).filter_by(id=bioent_id).first(), True)
     
    edges = []           
    for reference_id in top_references:
        for bioent_id in reference_id_to_bioent_ids[reference_id]:
            if bioent_id in nodes:
                edges.append(create_litguide_edge(bioent_id, reference_id))

    return {'nodes': nodes.values(), 'edges': edges}
