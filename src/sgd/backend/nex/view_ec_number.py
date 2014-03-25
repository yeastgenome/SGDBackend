from math import ceil

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.backend.nex.query_tools import get_all_bioconcept_children
from src.sgd.model.nex.bioentity import Protein
from src.sgd.model.nex.evidence import ECNumberevidence

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
            
    return [x.to_json() for x in ecevidences]