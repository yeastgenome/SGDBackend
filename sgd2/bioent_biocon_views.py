'''
Created on Feb 21, 2013

@author: kpaskov
'''
from jsonify.large import bioent_biocon_large
from jsonify.mini import reference_mini
from jsonify.small import phenoevidence_small
from model_new_schema.bioconcept import BioentBiocon, BioentBioconEvidence
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.table_maker import create_evidence_table_for_bioent_biocon
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload
 
@view_config(route_name='bioent_biocon', renderer='templates/bioent_biocon.pt')
def bioent_biocon_view(request):
    bioent_biocon_name = request.matchdict['bioent_biocon_name']
    bioent_biocon = DBSession.query(BioentBiocon).filter(BioentBiocon.name==bioent_biocon_name).first()
    json_bioent_biocon = bioent_biocon_large(bioent_biocon)
    return {'layout': site_layout(), 'page_title': json_bioent_biocon['basic_info']['name'], 'bioent_biocon': json_bioent_biocon}

@view_config(route_name='bioent_biocon_evidence', renderer='json')
def bioent_biocon_evidence_view(request):
    bioent_biocon_name = request.matchdict['bioent_biocon_name']
    bioent_biocon_id = DBSession.query(BioentBiocon).filter(BioentBiocon.name==bioent_biocon_name).first().id
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference')).filter(BioentBioconEvidence.bioent_biocon_id==bioent_biocon_id).all()
    evidence_jsons = [phenoevidence_small(bioent_biocon_evidence.evidence) for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE']
    return create_evidence_table_for_bioent_biocon(evidence_jsons)

@view_config(route_name='bioent_biocon_references', renderer='json')
def bioent_biocon_references_view(request):
    bioent_biocon_name = request.matchdict['bioent_biocon_name']
    bioent_biocon_id = DBSession.query(BioentBiocon).filter(BioentBiocon.name==bioent_biocon_name).first().id
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('evidence.reference')).filter(BioentBioconEvidence.bioent_biocon_id==bioent_biocon_id).all()
    references = set([bioent_biocon_evidence.evidence.reference for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE'])
    json_references = sorted([reference_mini(reference) for reference in references], key=lambda x: x['name'])
    return json_references