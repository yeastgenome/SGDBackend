from model_new_schema.bioconcept import Bioconcept, BioentBiocon
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Goevidence
from sgd2.models import DBSession
from sqlalchemy.orm import joinedload


def get_biocon(biocon_name, biocon_type):
    biocon_name = biocon_name.replace('_', ' ')
    biocon = DBSession.query(Bioconcept).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.official_name==biocon_name).first()
    return biocon

def get_bioent(bioent_name):
    bioent = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_name).first()
    return bioent

def get_bioent_biocons(biocon=None, bioent=None):
    if biocon is None and bioent is not None:
        bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioentity'), joinedload('bioconcept')).filter(BioentBiocon.bioent_id==bioent.id).all()
    elif biocon is None and bioent is None:
        bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioentity'), joinedload('bioconcept')).all()
    elif biocon is not None and bioent is None:
        bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioentity'), joinedload('bioconcept')).filter(BioentBiocon.biocon_id==biocon.id).all()
    elif biocon is not None and bioent is not None:
        bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioentity'), joinedload('bioconcept')).filter(BioentBiocon.biocon_id==biocon.id).filter(BioentBiocon.bioent_id==bioent.id).all()
    return bioent_biocons

def get_go_evidence(bioent_biocons):
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocons]
    evidences = DBSession.query(Goevidence).options(joinedload('reference')).filter(Goevidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    return evidences
