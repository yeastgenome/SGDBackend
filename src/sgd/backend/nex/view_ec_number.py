from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.model.nex.evidence import ECNumberevidence
import json

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_ec_number_evidence(locus_id, ec_number_id):
    query = DBSession.query(ECNumberevidence)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)
    if ec_number_id is not None:
        query = query.filter_by(ecnumber_id=ec_number_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, ec_number_id=None):
    if locus_id is None and ec_number_id is None:
        return {'Error': 'No locus_id or ec_number_id given.'}

    ecevidences = get_ec_number_evidence(locus_id=locus_id, ec_number_id=ec_number_id)

    if ecevidences is None:
        return {'Error': 'Too much data to display.'}
            
    return '[' + ', '.join([x.json for x in ecevidences if x.json is not None]) + ']'