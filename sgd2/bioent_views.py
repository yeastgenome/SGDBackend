'''
Created on Feb 20, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import BioentBioconEvidence, BioentBiocon
from model_new_schema.bioentity import Bioentity
from model_new_schema.link_maker import add_link
from pyramid.view import view_config
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload
from utils.graph import create_graph
from utils.utils import create_grouped_evidence_table, entry_with_note, \
    entry_with_link, create_phenotype_note

pp_rna_phenotypes = set(['protein-peptide accumulation', 'protein-peptide distribution', 'protein-peptide modification', 'RNA accumulation', 'RNA localization'])
chemical_phenotypes = set(['resistance to chemicals', 'chemical compound accumulation', 'chemical compund excretion'])


#------------------Basic Bioent Information-----------------------
def get_bioent(request):
    bioent_name = request.matchdict['bioent_name']
    bioent = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_name).first()
    return bioent

@view_config(route_name='bioent', renderer='templates/bioent.pt')
def bioent_view(request):
    bioent = get_bioent(request)
    return {'layout': site_layout(), 'page_title': bioent.name, 'bioent': bioent}

#------------------Biocon Information-----------------------
@view_config(route_name='bioent_all_biocon', renderer="json")
def bioent_all_biocon_view(request):
    bioent = get_bioent(request)
    bioent_biocons = DBSession.query(BioentBiocon).filter(BioentBiocon.bioent_id==bioent.id).options(joinedload('bioconcept')).all()
    bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in bioent_biocons]
    bioent_biocon_evidences = DBSession.query(BioentBioconEvidence).options(joinedload('evidence'), joinedload('bioent_biocon'), joinedload('evidence.reference'), joinedload('bioent_biocon.bioconcept'), joinedload('evidence.bioent_biocon_evidence')).filter(BioentBioconEvidence.bioent_biocon_id.in_(bioent_biocon_ids)).all()
    evidences = [bioent_biocon_evidence.evidence for bioent_biocon_evidence in bioent_biocon_evidences]
    tables = {}
    tables['phenotype'] = get_phenotypes(evidences)
    tables['chemical_phenotype'] = get_chemical_phenotypes(evidences)
    tables['pp_rna_phenotype'] = get_pp_rna_phenotypes(evidences)
    tables['go'] = get_gos(evidences)

    return tables

#-------GO Information------
def get_gos(bioent_biocons):
    bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.biocon_type == 'GO']
    return create_go_table(bioent_biocons)
    
def create_go_table(evidences):
    go_evidences = [evidence for evidence in evidences if evidence.evidence_type == 'GO_EVIDENCE']
    evidence_map = dict([(evidence.id, evidence.bioent_biocon.id) for evidence in go_evidences])
    def f(evs_for_group, group_term, bioent_biocon):
        total_entry = add_link(str(len(evs_for_group)), bioent_biocon.link)
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioconcept.go_aspect, total_entry]
    return create_grouped_evidence_table(go_evidences, evidence_map, f)

#-------Phenotype Information------
# Main phenotype information
def get_phenotypes(evidences):
    other_phenotypes = set()
    other_phenotypes.update(chemical_phenotypes)
    other_phenotypes.update(pp_rna_phenotypes)
    pheno_evidences = [evidence for evidence in evidences 
                if evidence.evidence_type == 'PHENOTYPE_EVIDENCE' and
                evidence.bioent_biocon_evidence.bioent_biocon.bioconcept.name not in other_phenotypes]
    evidence_map = dict([(evidence.id, evidence.bioent_biocon_evidence.bioent_biocon.id) for evidence in pheno_evidences])
    def f(evs_for_group, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evs_for_group]
        total_entry = entry_with_note(add_link(str(len(evs_for_group)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, total_entry]
        
    return create_grouped_evidence_table(pheno_evidences, evidence_map, f)

# Chemical Phenotype Information
def get_chemical_phenotypes(evidences):
    chem_evidences = [evidence for evidence in evidences 
                 if evidence.evidence_type == 'PHENOTYPE_EVIDENCE' and
                 evidence.bioent_biocon_evidence.bioent_biocon.bioconcept.name in chemical_phenotypes]
    evidence_map = dict([(evidence.id, ', '.join([chem.name for chem in evidence.chemicals])) for evidence in chem_evidences])
    def f(evs_for_group, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evs_for_group]
        total_entry = entry_with_note(add_link(str(len(evs_for_group)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, total_entry]
    
    return create_grouped_evidence_table(chem_evidences, evidence_map, f)

# Protein/peptide and RNA Phenotype Information
def get_pp_rna_phenotypes(evidences):
    pp_rna_evidences = [evidence for evidence in evidences 
                 if evidence.evidence_type == 'PHENOTYPE_EVIDENCE' and
                 evidence.bioent_biocon_evidence.bioent_biocon.bioconcept.name in pp_rna_phenotypes]
    evidence_map = dict([(evidence.id, evidence.reporter) for evidence in pp_rna_evidences])
    
    def f(evs_for_group, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evs_for_group]
        total_entry = entry_with_note(add_link(str(len(evs_for_group)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, total_entry]
    
    return create_grouped_evidence_table(pp_rna_evidences, evidence_map, f)

#------------------Biorel Information-----------------------
@view_config(route_name='bioent_all_biorel', renderer="json")
def bioent_all_biorel_view(request):
    bioent = get_bioent(request)
    
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
        biorel_entry = biorel.get_opposite(bioent).name_with_link
        total_entry = entry_with_link(str(biorel.evidence_count), biorel.link)
        table.append([biorel_entry, str(biorel.genetic_evidence_count), str(biorel.physical_evidence_count), total_entry])
    return table

#Cytoscape graph
@view_config(route_name='bioent_graph', renderer="json")
def bioent_graph_view(request):
    try:
        bioent = get_bioent(request)
        graph = create_graph(bioent)
        return graph
    except DBAPIError:
        return ['Error']


