'''
Created on Feb 20, 2013

@author: kpaskov
'''
from jsonify.graph import create_graph
from jsonify.large import bioent_large
from jsonify.small import bioent_biocon_small, biorel_small
from model_new_schema.bioconcept import BioentBiocon
from model_new_schema.bioentity import Bioentity
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.table_maker import create_bioent_biocon_table_for_bioent, \
    create_biorel_table_for_bioent, create_biorel_table_for_bioent2, \
    create_biorel_table_for_bioent3
from sgd2.views import site_layout
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload

@view_config(route_name='bioent', renderer='templates/bioent.pt')
def bioent_view(request):
    bioent_name = request.matchdict['bioent_name']
    
    bioent = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first()
    json_bioent = bioent_large(bioent)
    return {'layout': site_layout(), 'page_title': json_bioent['basic_info']['name'], 'bioent': json_bioent}

@view_config(route_name='bioent_phenotypes', renderer="json")
def bioent_phenotypes_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent_id = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first().id
    bioent_biocons = DBSession.query(BioentBiocon).options(joinedload('bioconcept')).filter(BioentBiocon.bioent_id==bioent_id).all()
    bioent_biocon_jsons = [bioent_biocon_small(bioent_biocon) for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.biocon_type == 'PHENOTYPE']
    return create_bioent_biocon_table_for_bioent(bioent_biocon_jsons)

@view_config(route_name='bioent_interactions', renderer="json")
def bioent_interactions_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first()
    interactions = [biorel_small(interaction) for interaction in bioent.biorelations if interaction.biorel_type == 'INTERACTION']
    return create_biorel_table_for_bioent(bioent_name, interactions)

@view_config(route_name='bioent_interactions2', renderer="json")
def bioent_interactions_view2(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first()
    interactions = [biorel_small(interaction) for interaction in bioent.biorelations if interaction.biorel_type == 'INTERACTION']
    return create_biorel_table_for_bioent2(bioent_name, interactions)

@view_config(route_name='bioent_interactions3', renderer="json")
def bioent_interactions_view3(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first()
    interactions = [biorel_small(interaction) for interaction in bioent.biorelations if interaction.biorel_type == 'INTERACTION']
    return create_biorel_table_for_bioent3(bioent_name, interactions)

@view_config(route_name='bioent_graph', renderer="json")
def bioent_graph_view(request):
    try:
        bioent_name = request.matchdict['bioent_name']
        bioent = DBSession.query(Bioentity).filter(Bioentity.name==bioent_name).first()
        graph = create_graph(bioent)
        return graph
    except DBAPIError:
        return ['Error']
    

