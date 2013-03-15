'''
Created on Feb 21, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import BioentBiocon
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Goevidence, Phenoevidence
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload

#------------------Basic Bioent Information-----------------------
def get_bioent_biocon(request):
    bioent_biocon_name = request.matchdict['bioent_biocon_name']
    biocon_type = request.matchdict['biocon_type'].upper()
    bioent_biocon = DBSession.query(BioentBiocon).filter(BioentBiocon.biocon_type==biocon_type).filter(BioentBiocon.official_name==bioent_biocon_name).first()
    
    if bioent_biocon is None:
        bioent_biocon = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_biocon_name).first()

    return bioent_biocon
    
@view_config(route_name='bioent_biocon', renderer='templates/bioent_biocon.pt')
def bioent_biocon_view(request):
    bioent_biocon = get_bioent_biocon(request)
    biocon_type = request.matchdict['biocon_type'].upper()
    
    evidence_link = request.url + '/evidence'
    
    go_graph_link = None
    if bioent_biocon.type == 'BIOENTITY' and biocon_type == 'GO':
        go_graph_link = bioent_biocon.go_graph_link
        
    return {'layout': site_layout(), 'page_title': bioent_biocon.name, 'bioent_biocon':bioent_biocon, 
            'evidence_link':evidence_link, 'biocon_type':biocon_type, 'go_graph_link':go_graph_link}


biocon_evidence_class = {'GO':Goevidence, 'PHENOTYPE': Phenoevidence}

#------------------Evidence Information-----------------------
@view_config(route_name='bioent_biocon_evidence', renderer='json')
def bioent_biocon_evidence_view(request):
    bioent_biocon = get_bioent_biocon(request)
    biocon_type = request.matchdict['biocon_type'].upper()
    cls = biocon_evidence_class[biocon_type]
            
    if bioent_biocon.type == 'BIOENTITY':
        bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocon.bioent_biocons if bioent_biocon.biocon_type == biocon_type]
        evidences = DBSession.query(cls).options(joinedload('bioent_biocon'), joinedload('reference'), joinedload('bioent_biocon.bioconcept')).filter(cls.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    else:
        bioent_biocon_id = bioent_biocon.id
        evidences = DBSession.query(cls).options(joinedload('bioent_biocon'), joinedload('reference')).filter(cls.bioent_biocon_id==bioent_biocon_id).all()
        
    tables = {}
    if biocon_type == 'PHENOTYPE':
        tables['evidence'] = create_evidence_table_for_phenotype(evidences)
    elif biocon_type == 'GO':
        tables['evidence'] = create_evidence_table_for_go(evidences)        
    tables['reference'] = get_references(evidences)
    return tables

def create_evidence_table_for_phenotype(evidences):
    table = []
    for evidence in evidences:
        bioent_biocon_entry = evidence.bioent_biocon.bioconcept.name_with_link
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
                      evidence.reporter, chemical_info, evidence.strain_id, evidence.source, reference_entry])
    return table

def create_evidence_table_for_go(evidences):  
    table = []
    for evidence in evidences:
        bioent_biocon_entry = evidence.bioent_biocon.bioconcept.name_with_link
        if evidence.reference is None:
            reference_entry = None
        else:
            reference_entry = evidence.reference.name_with_link
        
        table.append([bioent_biocon_entry, evidence.go_evidence, evidence.annotation_type, 
                      evidence.qualifier, evidence.source, 
                      reference_entry])
    return table

def get_references(evidences):
    references = set([evidence.reference for evidence in evidences if evidence.reference is not None])
    sorted_references = sorted(references, key=lambda x: x.name)
    citations = [reference.citation for reference in sorted_references]
    return citations