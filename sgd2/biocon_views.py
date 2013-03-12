'''
Created on Feb 21, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconcept, BioentBiocon
from pyramid.response import Response
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload
from utils.utils import entry_with_note, entry_with_link


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
    
    if biocon is None:
        return Response(status_int=500, body='Biocon could not be found.')
    
    bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioentity')).filter(BioentBiocon.biocon_id==biocon.id).all()
    tables = {}
    tables['bioent'] = get_bioents(bioent_biocons)
    return tables

def get_bioents(bioent_biocons):
    table = []
    for bioent_biocon in bioent_biocons:
        bioent_entry = bioent_biocon.bioentity.name_with_link
        
        evidence_desc = bioent_biocon.evidence_desc
        if evidence_desc:
            evidence_entry = entry_with_note(entry_with_link(str(bioent_biocon.evidence_count) , bioent_biocon.link), '(' + evidence_desc + ')')
        else:
            evidence_entry = entry_with_link(str(bioent_biocon.evidence_count) , bioent_biocon.link) 
        table.append([bioent_entry, evidence_entry])
    return table
