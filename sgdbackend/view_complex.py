from model_new_schema.bioentity import Complex
from model_new_schema.evidence import Complexevidence
from sgdbackend import view_go
from sgdbackend_query import get_evidence
from sgdbackend_query.query_auxiliary import get_biofacts

__author__ = 'kpaskov'

from sgdbackend_utils.cache import id_to_biocon, id_to_bioent


# -------------------------------Genes-----------------------------------------
def make_genes(complex_id):
    from sgdbackend_utils.cache import id_to_bioent
    bioent_ids = set([x.bioentity_id for x in get_evidence(Complexevidence, complex_id=complex_id)])
    return [id_to_bioent[x] for x in bioent_ids]


# -------------------------------Details---------------------------------------
def make_details(complex_id):
    return view_go.make_details(go_id=id_to_bioent[complex_id]['go']['id'])