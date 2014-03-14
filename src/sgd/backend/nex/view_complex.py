from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.evidence import Complexevidence
from src.sgd.backend.nex import view_go, DBSession, query_limit
from src.sgd.backend.nex.cache import get_obj, get_objs

__author__ = 'kpaskov'

# -------------------------------Genes-----------------------------------------
def get_complex_evidence(complex_id):
    query = DBSession.query(Complexevidence)
    if complex_id is not None:
        query = query.filter_by(complex_id=complex_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_genes(complex_id=None):
    if complex_id is None:
        return {'Error': 'No complex_id given.'}

    complex_evidences = get_complex_evidence(complex_id=complex_id)

    if complex_evidences is None:
        return {'Error': 'Too much data to display.'}

    bioent_ids = set([x.bioentity_id for x in complex_evidences])
    return get_objs(Bioentity, bioent_ids).values()

# -------------------------------Details---------------------------------------
def make_details(complex_id):
    return view_go.make_details(go_id=get_obj(Bioentity, complex_id)['go']['id'])