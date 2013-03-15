'''
Created on Feb 21, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconcept, BioentBiocon
from model_new_schema.evidence import Goevidence, Phenoevidence
from pyramid.response import Response
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload
from utils.utils import entry_with_note, entry_with_link, \
    create_note_from_pieces, create_grouped_evidence_table, create_phenotype_note


def get_biocon(request):
    biocon_name = request.matchdict['biocon_name']
    biocon_type = request.matchdict['biocon_type'].upper()
    biocon = DBSession.query(Bioconcept).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.official_name==biocon_name).first()
    return biocon

#------------------Basic Biocon Information-----------------------
@view_config(route_name='biocon', renderer='templates/biocon.pt')
def biocon_view(request):
    biocon = get_biocon(request)
    if biocon is None:
        return Response(status_int=500, body='Biocon could not be found.')
    return {'layout': site_layout(), 'page_title': biocon.name, 'biocon': biocon}

#------------------Bioent Information-----------------------
@view_config(route_name='biocon_all_bioent', renderer="json")
def bicon_all_bioent_view(request):
    biocon = get_biocon(request)
    biocon_type = request.matchdict['biocon_type'].upper()
    
    if biocon is None:
        return Response(status_int=500, body='Biocon could not be found.')
    
    bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioentity')).filter(BioentBiocon.biocon_id==biocon.id).all()
    if len(bioent_biocons) > 500:
        return {"aaData":get_bioents(bioent_biocons)}
    
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocons]
    if biocon_type == 'GO':
        evidences = DBSession.query(Goevidence).filter(Goevidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
        return {"aaData":get_go_bioents(evidences)}
    elif biocon_type == 'PHENOTYPE':
        evidences = DBSession.query(Phenoevidence).filter(Phenoevidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
        return {"aaData":get_phenotype_bioents(evidences)}

def get_bioents(bioent_biocons):
    table = []
    for bioent_biocon in bioent_biocons:
        bioent_entry = bioent_biocon.bioentity.name_with_link
        
        evidence_entry = entry_with_link(str(bioent_biocon.evidence_count) , bioent_biocon.link) 
        table.append([bioent_entry, evidence_entry])
    return table

def get_go_bioents(evidences):
    evidence_map = dict([(evidence.id, evidence.bioent_biocon.id) for evidence in evidences])
    def f(evs_for_group, group_term, bioent_biocon):
        evidence_codes = [ev.go_evidence for ev in evs_for_group]
        total_entry = entry_with_note(entry_with_link(str(len(evs_for_group)), bioent_biocon.link), create_note_from_pieces(evidence_codes))
        return [bioent_biocon.bioentity.name_with_link, total_entry]
    return create_grouped_evidence_table(evidences, evidence_map, f)

def get_phenotype_bioents(evidences):
    evidence_map = dict([(evidence.id, evidence.bioent_biocon.id) for evidence in evidences])
    def f(evs_for_group, group_term, bioent_biocon):
        qualifiers = [ev.qualifier for ev in evs_for_group]
        total_entry = entry_with_note(entry_with_link(str(len(evs_for_group)), bioent_biocon.link), create_phenotype_note(qualifiers))
        return [bioent_biocon.bioentity.name_with_link, total_entry]
    return create_grouped_evidence_table(evidences, evidence_map, f)
