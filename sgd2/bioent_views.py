'''
Created on Feb 20, 2013

@author: kpaskov
'''
from jsonify.graph import create_graph
from model_new_schema.bioconcept import BioentBioconEvidence, BioentBiocon
from model_new_schema.bioentity import Bioentity
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.table_maker import entry_with_note, entry_with_link
from sgd2.views import site_layout
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload

pp_rna_phenotypes = set(['protein-peptide accumulation', 'protein-peptide distribution', 'protein-peptide modification', 'RNA accumulation', 'RNA localization'])
chemical_phenotypes = set(['resistance to chemicals', 'chemical compound accumulation', 'chemical compund excretion'])


#------------------Basic Bioent Information-----------------------
@view_config(route_name='bioent', renderer='templates/bioent.pt')
def bioent_view(request):
    bioent_name = request.matchdict['bioent_name']
    
    bioent = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_name).first()
    return {'layout': site_layout(), 'page_title': bioent.name, 'bioent': bioent}

#------------------Biocon Information-----------------------
@view_config(route_name='bioent_all_biocon', renderer="json")
def bioent_all_biocon_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent_id = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_name).first().id
    bioent_biocons = DBSession.query(BioentBiocon).filter(BioentBiocon.bioent_id==bioent_id).options(joinedload('bioconcept')).all()
    
    tables = {}
    tables['phenotype'] = get_phenotypes(bioent_biocons)
    tables['chemical_phenotype'] = get_chemical_phenotypes(bioent_biocons)
    tables['pp_rna_phenotype'] = get_pp_rna_phenotypes(bioent_biocons)
    tables['go'] = get_gos(bioent_biocons)

    return tables

#-------GO Information------
def get_gos(bioent_biocons):
    bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.biocon_type == 'GO']
    return create_go_table_for_bioent(bioent_biocons)
    
def create_go_table_for_bioent(bioent_biocons):
    table = []
    for bioent_biocon in bioent_biocons:
        bioent_biocon_entry = bioent_biocon.name_for_bioent_with_link
        total_entry = entry_with_link(str(bioent_biocon.evidence_count), bioent_biocon.link)
        table.append([bioent_biocon_entry, bioent_biocon.bioconcept.go_aspect, total_entry])
    return table

#-------Phenotype Information------
# Main phenotype information
def get_phenotypes(bioent_biocons):
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.name not in pp_rna_phenotypes and bioent_biocon.bioconcept.name not in chemical_phenotypes]
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference'), joinedload('bioent_biocon.bioconcept'), joinedload('evidence.bioent_biocon_evidences')).filter(BioentBioconEvidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    evidences = [bioent_biocon_evidence.evidence for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE']
    evidence_map = dict([(evidence.id, evidence.bioent_biocon.id) for evidence in evidences])
    return create_phenotype_table_for_bioent(evidences, evidence_map, False)

# Chemical Phenotype Information
def get_chemical_phenotypes(bioent_biocons):
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.name in chemical_phenotypes]
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference'), joinedload('bioent_biocon.bioconcept'), joinedload('evidence.bioent_biocon_evidences')).filter(BioentBioconEvidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    evidences = [bioent_biocon_evidence.evidence for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE']
    evidence_map = dict([(evidence.id, ', '.join([chem.name for chem in evidence.chemicals])) for evidence in evidences])
    return create_phenotype_table_for_bioent(evidences, evidence_map, True)

# Protein/peptide and RNA Phenotype Information
def get_pp_rna_phenotypes(bioent_biocons):
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.name in pp_rna_phenotypes]
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference'), joinedload('bioent_biocon.bioconcept'), joinedload('evidence.bioent_biocon_evidences')).filter(BioentBioconEvidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    evidences = [bioent_biocon_evidence.evidence for bioent_biocon_evidence in bioent_biocon_evidences if bioent_biocon_evidence.evidence.evidence_type == 'PHENOTYPE_EVIDENCE']
    evidence_map = dict([(evidence.id, evidence.reporter) for evidence in evidences])
    return create_phenotype_table_for_bioent(evidences, evidence_map, True)

#Create phenotype tables
def create_phenotype_table_for_bioent(evidences, evidence_map, include_group_term=False):
    group_term_bioent_biocon = {}
    group_term_to_null_qualifiers = {}
    group_term_to_overexpression_qualifiers = {}
    group_term_to_conditional_qualifiers = {}
    group_term_to_all_qualifiers = {}
   
    for evidence in evidences:
        group_term = evidence_map[evidence.id]
        bb = evidence.bioent_biocon
        group_term_bioent_biocon[group_term] = bb
        mutant = evidence.mutant_type
        qualifier = evidence.qualifier
        if mutant == 'null':
            if group_term in group_term_to_null_qualifiers:
                group_term_to_null_qualifiers[group_term].append(qualifier)
            else:
                group_term_to_null_qualifiers[group_term] = [qualifier]
        if mutant == 'overexpression':
            if group_term in group_term_to_overexpression_qualifiers:
                group_term_to_overexpression_qualifiers[group_term].append(qualifier)
            else:
                group_term_to_overexpression_qualifiers[group_term] = [qualifier]
        if mutant == 'conditional':
            if group_term in group_term_to_conditional_qualifiers:
                group_term_to_conditional_qualifiers[group_term].append(qualifier)
            else:
                group_term_to_conditional_qualifiers[group_term] = [qualifier]
        if group_term in group_term_to_all_qualifiers:
            group_term_to_all_qualifiers[group_term].append(qualifier)
        else:
            group_term_to_all_qualifiers[group_term] = [qualifier]
        
    table = []
    for (group_term, bioent_biocon) in group_term_bioent_biocon.iteritems():
        bioent_biocon_name = bioent_biocon.name_for_bioent_with_link
        null_entry = '0'
        overex_entry = '0'
        cond_entry = '0'
        if group_term in group_term_to_null_qualifiers:
            quals = group_term_to_null_qualifiers[group_term]
            null_entry = entry_with_note(str(len(quals)), create_note(quals))
        if group_term in group_term_to_overexpression_qualifiers:
            quals = group_term_to_overexpression_qualifiers[group_term]
            overex_entry = entry_with_note(str(len(quals)), create_note(quals))
        if group_term in group_term_to_conditional_qualifiers:
            quals = group_term_to_conditional_qualifiers[group_term]
            cond_entry = entry_with_note(str(len(quals)), create_note(quals))
            
        quals = group_term_to_all_qualifiers[group_term]
            
        if include_group_term:
            total_entry = entry_with_note(str(len(quals)), create_note(quals))
            table.append([group_term, bioent_biocon_name, null_entry, overex_entry, cond_entry, total_entry])
        else:
            total_entry = entry_with_note(entry_with_link(str(len(quals)), bioent_biocon.link), create_note(quals))
            table.append([bioent_biocon_name, null_entry, overex_entry, cond_entry, total_entry])            
    return table

def create_note(qualifiers):
    increased_quals = set(['increased', 'increased rate', 'increased duration', 'premature'])
    decreased_quals = set(['delayed', 'decreased duration', 'decreased rate', 'decreased'])
    messages = []

    inc_count = 0
    dec_count = 0
    for qual in qualifiers:
        if qual in increased_quals:
            inc_count = inc_count + 1
        if qual in decreased_quals:
            dec_count = dec_count + 1

    if inc_count > 0:
        messages.append(str(inc_count) + unichr(11014))
    if dec_count > 0:
        messages.append(str(dec_count) + unichr(11015))
    
    message = ', '.join(messages)
    if len(message) > 0:
        return '(' + message + ')'
    else:
        return ''

#------------------Biorel Information-----------------------
@view_config(route_name='bioent_all_biorel', renderer="json")
def bioent_all_biorel_view(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_name).first()
    
    tables = {}
    tables['interaction'] = get_interactions(bioent)
    return tables

#-------Interaction Information------
def get_interactions(bioent):
    interactions = [interaction for interaction in bioent.biorelations if interaction.biorel_type == 'INTERACTION']
    return create_interaction_table(bioent, interactions)

def create_interaction_table(bioent, biorels):
    table = []
    for biorel in biorels:     
        biorel_entry = biorel.get_name_with_link_for(bioent)
        total_entry = entry_with_link(str(biorel.evidence_count), biorel.link)
        table.append([biorel_entry, str(biorel.genetic_evidence_count), str(biorel.physical_evidence_count), total_entry])
    return table

#Cytoscape graph
@view_config(route_name='bioent_graph', renderer="json")
def bioent_graph_view(request):
    try:
        bioent_name = request.matchdict['bioent_name']
        bioent = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_name).first()
        graph = create_graph(bioent)
        return graph
    except DBAPIError:
        return ['Error']



