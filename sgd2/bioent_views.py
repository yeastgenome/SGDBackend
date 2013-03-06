'''
Created on Feb 20, 2013

@author: kpaskov
'''
from jsonify.graph import create_graph
from jsonify.large import bioent_large
from jsonify.mini import goevidence_mini
from jsonify.small import bioent_biocon_small, biorel_small, phenoevidence_mid
from model_new_schema.bioconcept import BioentBiocon, BioentBioconEvidence
from model_new_schema.bioentity import Bioentity
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.table_maker import create_bioent_biocon_table_for_bioent, \
    create_biorel_table_for_bioent, create_go_table_for_bioent
from sgd2.views import site_layout
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload

pp_rna_phenotypes = set(['protein-peptide accumulation', 'protein-peptide distribution', 'protein-peptide modification', 'RNA accumulation', 'RNA localization'])
chemical_phenotypes = set(['resistance to chemicals', 'chemical compound accumulation', 'chemical compund excretion'])

@view_config(route_name='bioent', renderer='templates/bioent.pt')
def bioent_view(request):
    bioent_name = request.matchdict['bioent_name']
    
    bioent = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first()
    json_bioent = bioent_large(bioent)
    return {'layout': site_layout(), 'page_title': json_bioent['basic_info']['name'], 'bioent': json_bioent}

@view_config(route_name='bioent_phenotypes', renderer="json")
def bioent_phenotypes_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).options(joinedload('bioent_biocons')).filter(Bioentity.name==bioent_name).first()
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent.bioent_biocons if bioent_biocon.bioconcept.name not in pp_rna_phenotypes and bioent_biocon.bioconcept.name not in chemical_phenotypes]
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference'), joinedload('bioent_biocon.bioconcept'), joinedload('evidence.bioent_biocon_evidences')).filter(BioentBioconEvidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    evidence_jsons = [phenoevidence_mid(bioent_biocon_evidence.evidence) for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE']
    evidence_map = dict([(evidence['name'], evidence['bioent_biocon']['name']) for evidence in evidence_jsons])
    return create_bioent_biocon_table_for_bioent(evidence_jsons, evidence_map, False)

@view_config(route_name='bioent_interactions', renderer="json")
def bioent_interactions_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first()
    interactions = [biorel_small(interaction) for interaction in bioent.biorelations if interaction.biorel_type == 'INTERACTION']
    return create_biorel_table_for_bioent(bioent_name, interactions)

@view_config(route_name='bioent_chemical_phenotypes', renderer="json")
def bioent_chemical_phenotypes_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).options(joinedload('bioent_biocons')).filter(Bioentity.name==bioent_name).first()
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent.bioent_biocons if bioent_biocon.bioconcept.name in chemical_phenotypes]
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference'), joinedload('bioent_biocon.bioconcept'), joinedload('evidence.bioent_biocon_evidences')).filter(BioentBioconEvidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    evidence_jsons = [phenoevidence_mid(bioent_biocon_evidence.evidence) for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE']
    evidence_map = dict([(evidence['name'], ', '.join([chem[0] for chem in evidence['chemicals']])) for evidence in evidence_jsons])
    return create_bioent_biocon_table_for_bioent(evidence_jsons, evidence_map, True)

@view_config(route_name='bioent_pp_rna_phenotypes', renderer="json")
def bioent_pp_rna_phenotypes_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).options(joinedload('bioent_biocons')).filter(Bioentity.name==bioent_name).first()
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent.bioent_biocons if bioent_biocon.bioconcept.name in pp_rna_phenotypes]
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference'), joinedload('bioent_biocon.bioconcept'), joinedload('evidence.bioent_biocon_evidences')).filter(BioentBioconEvidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    evidence_jsons = [phenoevidence_mid(bioent_biocon_evidence.evidence) for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE']
    evidence_map = dict([(evidence['name'], evidence['reporter']) for evidence in evidence_jsons])
    return create_bioent_biocon_table_for_bioent(evidence_jsons, evidence_map, True)

@view_config(route_name='bioent_go', renderer="json")
def bioent_go_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).options(joinedload('bioent_biocons')).filter(Bioentity.name==bioent_name).first()
    bioent_biocons = [bioent_biocon for bioent_biocon in bioent.bioent_biocons if bioent_biocon.bioconcept.biocon_type == 'GO']
    return create_go_table_for_bioent(bioent_biocons)

@view_config(route_name='bioent_graph', renderer="json")
def bioent_graph_view(request):
    try:
        bioent_name = request.matchdict['bioent_name']
        bioent = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first()
        graph = create_graph(bioent)
        return graph
    except DBAPIError:
        return ['Error']
    

