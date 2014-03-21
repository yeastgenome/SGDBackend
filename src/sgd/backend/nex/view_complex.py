from src.sgd.model.nex.evidence import Complexevidence
from src.sgd.backend.nex import DBSession, query_limit

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_complex_evidence(locus_id, complex_id):
    query = DBSession.query(Complexevidence)
    if complex_id is not None:
        query = query.filter_by(complex_id=complex_id)
    if locus_id is not None:
        query = query.filter_by(bioentity_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, complex_id=None):
    if locus_id is None and complex_id is None:
        return {'Error': 'No locus_id or complex_id given.'}

    complex_evidences = get_complex_evidence(locus_id=locus_id, complex_id=complex_id)

    if complex_evidences is None:
        return {'Error': 'Too much data to display.'}

    return [x.to_json() for x in complex_evidences]
