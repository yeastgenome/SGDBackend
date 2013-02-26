'''
Created on Feb 21, 2013

@author: kpaskov
'''
from jsonify.large import biocon_large
from jsonify.small import bioent_biocon_small
from model_new_schema.bioconcept import Bioconcept, BioentBiocon
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.table_maker import create_bioent_biocon_table_for_biocon
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload

@view_config(route_name='biocon', renderer='templates/biocon.pt')
def biocon_view(request):
    biocon_name = request.matchdict['biocon_name']
    biocon = DBSession.query(Bioconcept).filter(Bioconcept.name==biocon_name).first()
    json_biocon = biocon_large(biocon)
    return {'layout': site_layout(), 'page_title': json_biocon['basic_info']['name'], 'biocon': json_biocon}

@view_config(route_name='biocon_genes', renderer="json")
def bicon_genes_view(request):
    biocon_name = request.matchdict['biocon_name']
    biocon_id = DBSession.query(Bioconcept).filter(Bioconcept.name==biocon_name).first().id
    bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioentity')).filter(BioentBiocon.biocon_id==biocon_id).all()
    bioent_biocon_jsons = [bioent_biocon_small(bioent_biocon) for bioent_biocon in bioent_biocons]
    return create_bioent_biocon_table_for_biocon(bioent_biocon_jsons)