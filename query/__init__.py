from model_new_schema.bioconcept import Bioconcept, BioentBiocon, BioconAncestor, \
    BioconBiocon
from model_new_schema.bioentity import Bioentity
from model_new_schema.biorelation import Biorelation
from model_new_schema.evidence import Goevidence, Phenoevidence, Interevidence
from model_new_schema.reference import Reference
from sgd2.models import DBSession
from sqlalchemy.orm import joinedload
import math


def get_biocon(biocon_name, biocon_type):
    biocon = DBSession.query(Bioconcept).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.official_name==biocon_name).first()
    return biocon

def get_bioent(bioent_name):
    bioent = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_name).first()
    return bioent

def get_biorel(biorel_name, biorel_type):
    biorel = DBSession.query(Biorelation).filter(Biorelation.biorel_type==biorel_type).filter(Biorelation.official_name==biorel_name).first()
    return biorel

def get_reference(reference_name):
    reference = None
    try:
        float(reference_name)
        reference = DBSession.query(Reference).filter(Reference.pubmed_id == reference_name).first() 
        if reference is None:
            reference = DBSession.query(Reference).filter(Reference.id == reference_name).first()
    except:
        pass
    if reference is None:
        reference = DBSession.query(Reference).filter(Reference.dbxref_id == reference_name).first() 
    return reference
      

def get_biorels(biorel_type, bioent):
    return [biorel for biorel in bioent.biorelations if biorel.biorel_type == biorel_type]

#Used for interaction graph
def get_interactions(bioent_ids):
    interactions = set(DBSession.query(Biorelation).filter(Biorelation.biorel_type=='INTERACTION').filter(Biorelation.source_bioent_id.in_(bioent_ids)).all())
    interactions.update(DBSession.query(Biorelation).filter(Biorelation.biorel_type=='INTERACTION').filter(Biorelation.sink_bioent_id.in_(bioent_ids)).all())
    return interactions

def get_bioent_biocons(biocon_type, biocon=None, bioent=None):
    if biocon is None and bioent is None:
        raise Exception()
    
    query = DBSession.query(BioentBiocon).options(joinedload('bioentity'), joinedload('bioconcept')).filter(BioentBiocon.biocon_type==biocon_type)
    if bioent is not None:
        query = query.filter(BioentBiocon.bioent_id==bioent.id)
    if biocon is not None:
        query = query.filter(BioentBiocon.biocon_id==biocon.id)
    return query.all()

def get_biocon_family(biocon):
    family = set([biocon])

    biocon_ancs = DBSession.query(BioconAncestor).options(joinedload('ancestor_biocon')).filter(BioconAncestor.child_biocon_id==biocon.id).all()
    family.update([biocon_anc.ancestor_biocon for biocon_anc in biocon_ancs])
    
    biocon_children = DBSession.query(BioconBiocon).options(joinedload('child_biocon')).filter(BioconBiocon.parent_biocon_id==biocon.id).all()
    family.update([biocon_child.child_biocon for biocon_child in biocon_children])
    
    child_ids = set([biocon_child.child_biocon.id for biocon_child in biocon_children])
    all_ids = set([b.id for b in family])
    
    return {'family':family, 'child_ids':child_ids, 'all_ids':all_ids}

def get_biocon_biocons(biocon_ids):
    biocon_ids = set(biocon_ids)
    related_biocon_biocons = set()
    
    ancestor_in_list = DBSession.query(BioconBiocon).filter(BioconBiocon.parent_biocon_id.in_(biocon_ids)).all()
    related_biocon_biocons.update([biocon_biocon for biocon_biocon in ancestor_in_list if biocon_biocon.child_biocon_id in biocon_ids])
    
    child_in_list = DBSession.query(BioconBiocon).filter(BioconBiocon.child_biocon_id.in_(biocon_ids)).all()
    related_biocon_biocons.update([biocon_biocon for biocon_biocon in child_in_list if biocon_biocon.parent_biocon_id in biocon_ids])
    
    return related_biocon_biocons

def get_related_bioent_biocons(biocon_ids):
    bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioentity'), joinedload('bioconcept')).filter(BioentBiocon.biocon_id.in_(biocon_ids)).all()
    return bioent_biocons

#Get Evidence
chunk_size = 500
def get_go_evidence(bioent_biocons):
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocons]
    num_chunks = int(math.ceil(float(len(bioent_biocons))/chunk_size))
    evidences = set()
    for i in range(0, num_chunks):
        min_index = i*chunk_size
        max_index = (i+1)*chunk_size
        if max_index > len(bioent_biocons):
            chunk_bioent_biocon_ids = bioent_biocon_ids[min_index:]
        else:
            chunk_bioent_biocon_ids = bioent_biocon_ids[min_index:max_index]
        evidences.update(DBSession.query(Goevidence).options(joinedload('reference')).filter(Goevidence.bioent_biocon_id.in_(chunk_bioent_biocon_ids)).all())
    return evidences

def get_go_evidence_ref(reference):
    return set(DBSession.query(Goevidence).options(joinedload('reference')).filter(Goevidence.reference_id==reference.id).all())

def get_phenotype_evidence(bioent_biocons):
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocons]
    num_chunks = int(math.ceil(float(len(bioent_biocons))/chunk_size))
    evidences = set()
    for i in range(0, num_chunks):
        min_index = i*chunk_size
        max_index = (i+1)*chunk_size
        if max_index > len(bioent_biocons):
            chunk_bioent_biocon_ids = bioent_biocon_ids[min_index:]
        else:
            chunk_bioent_biocon_ids = bioent_biocon_ids[min_index:max_index]
        evidences.update(DBSession.query(Phenoevidence).options(joinedload('reference'), joinedload('allele'), joinedload('phenoev_chemicals')).filter(Phenoevidence.bioent_biocon_id.in_(chunk_bioent_biocon_ids)).all())
    return evidences

def get_phenotype_evidence_ref(reference):
    return set(DBSession.query(Phenoevidence).options(joinedload('reference'), joinedload('allele'), joinedload('phenoev_chemicals'), joinedload('bioent_biocon'), joinedload('bioent_biocon.bioentity')).filter(Phenoevidence.reference_id==reference.id).all())

def get_interaction_evidence(biorels):
    biorel_ids = [biorel.id for biorel in biorels]
    num_chunks = int(math.ceil(float(len(biorels))/chunk_size))
    evidences = set()
    for i in range(0, num_chunks):
        min_index = i*chunk_size
        max_index = (i+1)*chunk_size
        if max_index > len(biorels):
            chunk_biorel_ids = biorel_ids[min_index:]
        else:
            chunk_biorel_ids = biorel_ids[min_index:max_index]
        evidences.update(DBSession.query(Interevidence).options(joinedload('reference')).filter(Interevidence.biorel_id.in_(chunk_biorel_ids)).all())
    return evidences

def get_interaction_evidence_ref(reference):
    return set(DBSession.query(Interevidence).options(joinedload('reference')).filter(Interevidence.reference_id==reference.id).all())


