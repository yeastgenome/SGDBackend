from math import ceil

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.backend.nex.query_tools import get_all_bioconcept_children
from src.sgd.model.nex.bioconcept import Phenotype
from src.sgd.model.nex.evidence import Phenotypeevidence, Chemicalproperty
from sqlalchemy.orm import joinedload
import json

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_phenotype_evidence(locus_id, phenotype_id, observable_id, chemical_id, reference_id, with_children):
    query = DBSession.query(Phenotypeevidence)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)
    if phenotype_id is not None:
        query = query.filter_by(phenotype_id=phenotype_id)
    if observable_id is not None:
        if with_children:
            phenotype_ids = set()
            for new_observable_id in list(get_all_bioconcept_children(observable_id)):
                phenotype_ids.update([x.id for x in DBSession.query(Phenotype.id).filter_by(observable_id=new_observable_id).all()])
        else:
            phenotype_ids = set([x.id for x in DBSession.query(Phenotype.id).filter_by(observable_id=observable_id).all()])

        phenotype_ids = list(phenotype_ids)
        num_chunks = int(ceil(1.0*len(phenotype_ids)/500))
        evidences = []
        for i in range(num_chunks):
            subquery = query.filter(Phenotypeevidence.phenotype_id.in_(phenotype_ids[i*500:(i+1)*500]))
            if len(evidences) + subquery.count() > query_limit:
                return None
            evidences.extend(subquery.all())
        return evidences
    if chemical_id is not None:
        chemical_evidence_ids = list(set([x.evidence_id for x in DBSession.query(Chemicalproperty).filter_by(bioitem_id=chemical_id).all()]))
        num_chunks = int(ceil(1.0*len(chemical_evidence_ids)/500))
        evidences = []
        for i in range(num_chunks):
            subquery = query.filter(Phenotypeevidence.id.in_(chemical_evidence_ids[i*500:(i+1)*500]))
            if len(evidences) + subquery.count() > query_limit:
                return None
            evidences.extend(subquery.all())
        return evidences
    else:
        if query.count() > query_limit:
            return None
        return query.all()

def make_details(locus_id=None, phenotype_id=None, observable_id=None, chemical_id=None, reference_id=None, with_children=False):
    if locus_id is None and phenotype_id is None and observable_id is None and chemical_id is None and reference_id is None:
        return {'Error': 'No locus_id or phenotype_id or observable_id or chemical_id or reference_id given.'}

    phenoevidences = get_phenotype_evidence(locus_id=locus_id, phenotype_id=phenotype_id, observable_id=observable_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)

    if phenoevidences is None:
        return json.dumps({'Error': 'Too much data to display.'})

    #return '[' + ', '.join([x.json for x in phenoevidences if x.json is not None]) + ']'
    return json.dumps([x.to_json() for x in phenoevidences])
