from math import ceil

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.model.nex.evidence import Expressiondata
from sqlalchemy.orm import joinedload
import json

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_expression_evidence(locus_id):
    query = DBSession.query(Expressiondata).options(joinedload('evidence'), joinedload('locus'))
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    expressionevidences = get_expression_evidence(locus_id=locus_id)

    if expressionevidences is None:
        return {'Error': 'Too much data to display.'}

    return '[' + ', '.join([x.json for x in expressionevidences if x.json is not None]) + ']'
