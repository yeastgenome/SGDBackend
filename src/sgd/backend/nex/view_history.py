from src.sgd.model.nex.bioentity import Locus
from src.sgd.model.nex.bioitem import Domain
from src.sgd.model.nex.evidence import Historyevidence
from src.sgd.backend.nex import DBSession, query_limit
from sqlalchemy.orm import joinedload
import json

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_history_evidence(locus_id):
    query = DBSession.query(Historyevidence)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    history_evidences = get_history_evidence(locus_id=locus_id)

    if history_evidences is None:
        return {'Error': 'Too much data to display.'}

    return '[' + ', '.join([x.json for x in history_evidences if x.json is not None]) + ']'
