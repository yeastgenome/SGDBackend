'''
Created on Feb 21, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.biorelation import Biorelation
from model_new_schema.evidence import Interevidence
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload, subqueryload
 
#------------------Basic Biorel Information-----------------------
def get_biorel(request):
    biorel_name = request.matchdict['biorel_name']
    biorel_type = request.matchdict['biorel_type'].upper()
    biorel = DBSession.query(Biorelation).options(subqueryload('source_bioent'), subqueryload('sink_bioent')).filter(Biorelation.biorel_type==biorel_type).filter(Biorelation.official_name==biorel_name).first()
    
    if biorel is None:
        biorel = DBSession.query(Bioentity).filter(Bioentity.official_name==biorel_name).first()

    return biorel

@view_config(route_name='biorel', renderer='templates/biorel.pt')
def biorel_view(request):
    biorel = get_biorel(request)
    biorel_type = request.matchdict['biorel_type'].upper()
    evidence_link = request.url + '/evidence'
    return {'layout': site_layout(), 'page_title': biorel.name, 'biorel': biorel, 'evidence_link':evidence_link, 'biorel_type':biorel_type}

#------------------Evidence for Interactions-----------------------
@view_config(route_name='biorel_evidence', renderer='json')
def biorel_evidence_view(request):
    biorel = get_biorel(request)
    
    if biorel.type == 'BIORELATION':
        bioent = None
        biorel_id = biorel.id
        interevidences = DBSession.query(Interevidence).options(joinedload('biorel'), joinedload('reference')).filter(Interevidence.biorel_id==biorel_id).all()
    else:
        bioent = biorel
        biorel_ids = [biorel.id for biorel in bioent.biorelations]
        interevidences = DBSession.query(Interevidence).options(joinedload('biorel'), joinedload('reference')).filter(Interevidence.biorel_id.in_(biorel_ids)).all()
           
    tables = {}
    tables['genetic_evidence'] = get_genetic_evidence(interevidences, bioent)
    tables['physical_evidence'] = get_physical_evidence(interevidences, bioent)
    tables['reference']  = get_reference(interevidences)
    return tables

def get_genetic_evidence(interevidences, bioent):
    gen_evidences = set([evidence for evidence in interevidences 
                         if evidence.interaction_type == 'genetic'])
    return create_evidence_table_for_interaction(gen_evidences, bioent, True)

def get_physical_evidence(interevidences, bioent):
    phys_evidences = set([evidence for evidence in interevidences 
                          if evidence.interaction_type == 'physical'])
    return create_evidence_table_for_interaction(phys_evidences, bioent, False)

def create_evidence_table_for_interaction(evidences, bioent, is_genetic):
    table = []
    for evidence in evidences:
        reference_entry = evidence.reference.name_with_link
        phenotype = evidence.phenotype
            
        if bioent is None:
            bioent_entry = None
            direction = evidence.direction
        else:
            biorel = evidence.biorel
            bioent_entry = biorel.get_opposite(bioent).name_with_link

            if biorel.source_bioent == bioent:
                direction = evidence.direction
            else:
                direction = reverse_direction(evidence.direction)
        
        if is_genetic:
            table.append([bioent_entry, evidence.experiment_type, evidence.annotation_type, direction, phenotype, reference_entry])
        else:
            table.append([bioent_entry, evidence.experiment_type, evidence.annotation_type, direction, evidence.modification, reference_entry])
            
    return table

def reverse_direction(direction):
    if direction == 'bait-hit':
        return 'hit-bait'
    else:
        return 'bait-hit'

#------------------Reference Information-----------------------
def get_reference(interevidences):
    references = set([evidence.reference for evidence in interevidences])
    sorted_references = sorted(references, key=lambda x: x.name)
    citations = [reference.citation for reference in sorted_references]
    return citations