from src.sgd.model.nex.bioentity import Locus
from src.sgd.model.nex.bioitem import Domain
from src.sgd.model.nex.evidence import Domainevidence, Phosphorylationevidence, Proteinexperimentevidence
from src.sgd.backend.nex import DBSession, query_limit
from sqlalchemy.orm import joinedload
import json

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_protein_domain_evidence(locus_id, domain_id):
    query = DBSession.query(Domainevidence).options(joinedload('domain'))
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)
    if domain_id is not None:
        query = query.filter_by(domain_id=domain_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, domain_id=None):
    if locus_id is None and domain_id is None:
        return {'Error': 'No locus_id or domain_id given.'}

    if locus_id is not None:
        domain_evidences = get_protein_domain_evidence(locus_id=locus_id, domain_id=domain_id)
    else:
        domain_evidences = get_protein_domain_evidence(locus_id=None, domain_id=domain_id)

    if domain_evidences is None:
        return {'Error': 'Too much data to display.'}

    domain_evidences = [x for x in domain_evidences if x.domain.display_name != 'seg']

    return '[' + ', '.join([x.json for x in domain_evidences if x.json is not None]) + ']'

# -------------------------------Details---------------------------------------
def get_phosphorylation_evidence(locus_id):
    query = DBSession.query(Phosphorylationevidence)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_phosphorylation_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    return '[' + ', '.join([x.json for x in sorted(get_phosphorylation_evidence(locus_id=locus_id), key=lambda x: x.site_index) if x.json is not None]) + ']'

# -------------------------------Details---------------------------------------
def get_protein_experiment_evidence(locus_id):
    query = DBSession.query(Proteinexperimentevidence)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_protein_experiment_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}
    return '[' + ', '.join([x.json for x in get_protein_experiment_evidence(locus_id=locus_id) if x.json is not None]) + ']'