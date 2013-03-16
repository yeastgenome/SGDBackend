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


def get_biocon(request, biocon_type):
    biocon_name = request.matchdict['biocon_name'].replace('_', ' ')
    biocon = DBSession.query(Bioconcept).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.official_name==biocon_name).first()
    return biocon

#------------------Basic Biocon Information-----------------------
@view_config(route_name='biocon', renderer='templates/biocon.pt')
def biocon_view(request):
    biocon = get_biocon(request)
    if biocon is None:
        return Response(status_int=500, body='Biocon could not be found.')
    return {'layout': site_layout(), 'page_title': biocon.name, 'biocon': biocon}



@view_config(route_name='phenotype', renderer='templates/phenotype.pt')
def phenotype_view(request):
    biocon = get_biocon(request, 'PHENOTYPE')
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
        return make_go_table(evidences, True)
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

def make_go_table(evidences, include_comp):
    tables = {}

    if not include_comp:
        evidences = [evidence for evidence in evidences if evidence.annotation_type != 'computational']
        tables['computational'] = make_comp_count_go_table(evidences)

    tables['go_p'] = make_single_go_table(evidences, 'biological process')
    tables['go_f'] = make_single_go_table(evidences, 'molecular function')
    tables['go_c'] = make_single_go_table(evidences, 'cellular component')
    return tables

def make_single_go_table(evidences, namespace):
    goevidences = [evidence for evidence in evidences if evidence.bioent_biocon.bioconcept.go_aspect == namespace]
    evidence_map = dict([(evidence.id, evidence.bioent_biocon.id) for evidence in goevidences])
    def f(evs_for_group, group_term, bioent_biocon):
        evidence_codes = set([ev.go_evidence for ev in evs_for_group])
        ev_code_message = ', '.join(sorted(evidence_codes))    
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, ev_code_message]
    return create_grouped_evidence_table(goevidences, evidence_map, f)

def make_comp_count_go_table(goevidences):
    return len(set([evidence.bioent_biocon for evidence in goevidences if evidence.annotation_type == 'computational']))

def get_phenotype_bioents(evidences):
    evidence_map = dict([(evidence.id, evidence.bioent_biocon.id) for evidence in evidences])
    def f(evs_for_group, group_term, bioent_biocon):
        qualifiers = [ev.qualifier for ev in evs_for_group]
        total_entry = entry_with_note(entry_with_link(str(len(evs_for_group)), bioent_biocon.link), create_phenotype_note(qualifiers))
        return [bioent_biocon.bioentity.name_with_link, total_entry]
    return create_grouped_evidence_table(evidences, evidence_map, f)
