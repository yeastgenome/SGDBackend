from src.sgd.backend.nex import create_simple_table, DBSession, query_limit

from src.sgd.model.nex.evidence import Bindingevidence
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.backend.nex.cache import get_obj
from src.sgd.backend.nex.obj_to_json import minimize_json, evidence_to_json

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_binding_evidence(locus_id):
    query = DBSession.query(Bindingevidence)
    if locus_id is not None:
        query = query.filter_by(bioentity_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    binding_site_evidences = get_binding_evidence(locus_id=locus_id)

    if binding_site_evidences is None:
        return {'Error': 'Too much data to display.'}

    return create_simple_table(binding_site_evidences, make_evidence_row) 

def make_evidence_row(binding_evidence): 
    obj_json = evidence_to_json(binding_evidence).copy()
    obj_json['bioentity'] = minimize_json(get_obj(Bioentity, binding_evidence.bioentity_id), include_format_name=True)
    obj_json['total_score'] = binding_evidence.total_score
    obj_json['expert_confidence'] = binding_evidence.expert_confidence
    obj_json['img_url'] = binding_evidence.link
    obj_json['motif_id'] = binding_evidence.motif_id
    return obj_json