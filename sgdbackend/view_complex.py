from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Complexevidence
from sgdbackend import view_go
from sgdbackend_query import get_evidence
from sgdbackend_utils.cache import get_obj, get_objs

__author__ = 'kpaskov'


# -------------------------------Genes-----------------------------------------
def make_genes(complex_id):
    bioent_ids = set([x.bioentity_id for x in get_evidence(Complexevidence, complex_id=complex_id)])
    return get_objs(Bioentity, bioent_ids).values()


# -------------------------------Details---------------------------------------
def make_details(complex_id):
    return view_go.make_details(go_id=get_obj(Bioentity, complex_id)['go']['id'])