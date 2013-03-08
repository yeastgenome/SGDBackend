'''
Created on Feb 21, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.biorelation import Biorelation, BiorelEvidence
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload, subqueryload
from string import upper
 
#------------------Basic Biorel Information-----------------------
@view_config(route_name='biorel', renderer='templates/biorel.pt')
def biorel_view(request):
    biorel_name = request.matchdict['biorel_name']
    biorel_type = upper(request.matchdict['biorel_type'])
    biorel = DBSession.query(Biorelation).options(subqueryload('source_bioent'), subqueryload('sink_bioent')).filter(Biorelation.biorel_type==biorel_type).filter(Biorelation.official_name==biorel_name).first()
    
    if biorel is None:
        biorel = DBSession.query(Bioentity).filter(Bioentity.name==biorel_name).first()
    
    if biorel is None:
        request.response.status = '404 Not Found'
        return {'URL':request.URL}
    
    return {'layout': site_layout(), 'page_title': biorel.name, 'biorel': biorel}

#------------------Evidence for Interactions-----------------------
@view_config(route_name='biorel_evidence', renderer='json')
def biorel_evidence_view(request):
    biorel_name = request.matchdict['biorel_name']
    biorel_type = upper(request.matchdict['biorel_type'])
    biorel = DBSession.query(Biorelation).filter(Biorelation.biorel_type==biorel_type).filter(Biorelation.official_name==biorel_name).first()
    
    if biorel is not None:
        biorel_id = biorel.id
        bioent = None
        evidences = DBSession.query(BiorelEvidence).options(joinedload('evidence'), joinedload('evidence.reference'), joinedload('biorel'), joinedload('evidence.biorel_evidence')).filter(BiorelEvidence.biorel_id==biorel_id).all()
    else:
        bioent = DBSession.query(Bioentity).filter(Bioentity.name==biorel_name).first()
        if bioent is not None:
            biorel_ids = [biorel.id for biorel in bioent.biorelations]
            evidences = DBSession.query(BiorelEvidence).options(joinedload('evidence'), joinedload('evidence.reference'), joinedload('biorel'), joinedload('evidence.biorel_evidence')).filter(BiorelEvidence.biorel_id.in_(biorel_ids)).all()
           
    tables = {}
    tables['genetic_evidence'] = get_genetic_evidence(evidences, bioent)
    tables['physical_evidence'] = get_physical_evidence(evidences, bioent)
    tables['reference']  = get_reference(evidences)
    return tables

def get_genetic_evidence(evidences, bioent):
    gen_evidences = set([biorel_evidence.evidence for biorel_evidence in evidences if biorel_evidence.evidence.evidence_type == 'INTERACTION_EVIDENCE' and biorel_evidence.evidence.interaction_type == 'genetic'])
    return create_evidence_table_for_interaction(gen_evidences, bioent, True)

def get_physical_evidence(evidences, bioent):
    phys_evidences = set([biorel_evidence.evidence for biorel_evidence in evidences if biorel_evidence.evidence.evidence_type == 'INTERACTION_EVIDENCE' and biorel_evidence.evidence.interaction_type == 'physical'])
    return create_evidence_table_for_interaction(phys_evidences, bioent, False)

def create_evidence_table_for_interaction(evidences, bioent, is_genetic):
    table = []
    for evidence in evidences:
        reference_entry = evidence.reference.name_with_link
        phenotype = evidence.phenotype
            
        if bioent is None:
            biorel_entry = None
            direction = evidence.direction
        else:
            biorel = evidence.biorel
            biorel_entry = biorel.get_name_with_link_for(bioent)

            if biorel.source == bioent:
                direction = evidence.direction
            else:
                direction = reverse_direction(evidence.direction)
        
        if is_genetic:
            table.append([biorel_entry, evidence.experiment_type, evidence.annotation_type, direction, phenotype, reference_entry])
        else:
            table.append([biorel_entry, evidence.experiment_type, evidence.annotation_type, direction, evidence.modification, reference_entry])
            
    return table

def reverse_direction(direction):
    if direction == 'bait-hit':
        return 'hit-bait'
    else:
        return 'bait-hit'

#------------------Reference Information-----------------------
def get_reference(evidences):
    references = set([biorel_evidence.evidence.reference for biorel_evidence in evidences if biorel_evidence.evidence.evidence_type == 'INTERACTION_EVIDENCE'])
    sorted_references = sorted(references, key=lambda x: x.name)
    citations = [reference.citation for reference in sorted_references]
    return citations