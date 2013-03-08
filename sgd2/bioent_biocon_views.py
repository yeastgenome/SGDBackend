'''
Created on Feb 21, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import BioentBioconEvidence, BioentBiocon
from model_new_schema.bioentity import Bioentity
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload

@view_config(route_name='bioent_biocon', renderer='templates/bioent_biocon.pt')
def bioent_biocon_view(request):
    bioent_biocon_name = request.matchdict['bioent_biocon_name']
    biocon_type = request.matchdict['biocon_type'].upper()
    bioent_biocon = DBSession.query(BioentBiocon).filter(BioentBiocon.biocon_type==biocon_type).filter(BioentBiocon.official_name==bioent_biocon_name).first()
    if bioent_biocon is None:
        bioent_biocon = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_biocon_name).first()
        evidence_link = bioent_biocon.all_phenotype_link + '/evidence'
    else:
        evidence_link = bioent_biocon.evidence_link
    return {'layout': site_layout(), 'page_title': bioent_biocon.name, 'bioent_biocon':bioent_biocon, 'evidence_link':evidence_link, 'biocon_type':biocon_type}

@view_config(route_name='bioent_biocon_evidence', renderer='json')
def bioent_biocon_evidence_view(request):
    bioent_biocon_name = request.matchdict['bioent_biocon_name']
    biocon_type = request.matchdict['biocon_type'].upper()
    bioent_biocon = DBSession.query(BioentBiocon).filter(BioentBiocon.biocon_type==biocon_type).filter(BioentBiocon.official_name==bioent_biocon_name).first()
    if bioent_biocon is not None:
        bioent_biocon_id = bioent_biocon.id
        bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference')).filter(BioentBioconEvidence.bioent_biocon_id==bioent_biocon_id).all()
    else:
        bioent = DBSession.query(Bioentity).options(joinedload('bioent_biocons')).filter(Bioentity.official_name==bioent_biocon_name).first()
        if bioent is not None:
            bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent.bioent_biocons if bioent_biocon.biocon_type == biocon_type]
            bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference'), joinedload('bioent_biocon.bioconcept'), joinedload('evidence.bioent_biocon_evidences')).filter(BioentBioconEvidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    evidences = [bioent_biocon_evidence.evidence for bioent_biocon_evidence in bioent_biocon_evidences]
    
    tables = {}
    if biocon_type == 'PHENOTYPE':
        tables['evidence'] = create_evidence_table_for_phenotype(evidences)
    elif biocon_type == 'GO':
        tables['evidence'] = create_evidence_table_for_go(evidences)        
    tables['reference'] = get_references(bioent_biocon_evidences)
    return tables

def create_evidence_table_for_phenotype(evidences):
    table = []
    for evidence in evidences:
        bioent_biocon_entry = evidence.bioent_biocon.name_with_link
        if evidence.allele:
            allele_entry = evidence.allele.name_with_link
        else:
            allele_entry = None
        reference_entry = evidence.reference.name_with_link
        
        chemicals = []
        for chemical in evidence.phenoev_chemicals:
            if chemical.chemical_amt is None:
                chemicals.append(chemical.chemical_name)
            else:
                chemicals.append(chemical.chemical_name + ': ' + chemical.chemical_amt)
        chemical_info = ', '.join(chemicals)
        
        table.append([bioent_biocon_entry, evidence.qualifier, evidence.experiment_type, evidence.mutant_type, allele_entry, 
                      evidence.reporter, chemical_info, evidence.strain_id, reference_entry])
    return table

def create_evidence_table_for_go(evidences):
    table = []
    for evidence in evidences:
        bioent_biocon_entry = evidence.bioent_biocon.name_with_link
        reference_entry = evidence.reference.name_with_link
        
        table.append([bioent_biocon_entry, evidence.go_evidence, evidence.annotation_type, evidence.source, evidence.date_last_reviewed, 
                      evidence.qualifier, evidence.strain_id, reference_entry])
    return table

def get_references(bioent_biocon_evidences):
    references = set([bioent_biocon_evidence.evidence.reference for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE'])
    sorted_references = sorted(references, key=lambda x: x.name)
    citations = [reference.citation for reference in sorted_references]
    return citations