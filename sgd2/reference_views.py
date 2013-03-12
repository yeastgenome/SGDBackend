'''
Created on Feb 21, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Evidence
from model_new_schema.reference import Reference
from pyramid.view import view_config
from sgd2.bioent_views import pp_rna_phenotypes, chemical_phenotypes
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.orm import joinedload
from utils.utils import create_grouped_evidence_table, entry_with_note, \
    entry_with_link, create_phenotype_note
 
 
#------------------Basic Reference Information-----------------------
def get_reference(request):
    ref_id = request.matchdict['pubmed_id']
    reference = None
    try:
        float(ref_id)
        reference = DBSession.query(Reference).filter(Reference.pubmed_id == ref_id).first() 
        if reference is None:
            reference = DBSession.query(Reference).filter(Reference.id == ref_id).first()
    except:
        pass
    if reference is None:
        reference = DBSession.query(Reference).filter(Reference.dbxref_id == ref_id).first() 
    return reference
        

@view_config(route_name='reference', renderer='templates/reference.pt')
def reference_view(request):
    reference = get_reference(request)    
    return {'layout': site_layout(), 'page_title': reference.name, 'ref': reference}

#------------------Evidence Information-----------------------
@view_config(route_name='reference_all_evidence', renderer="json")
def reference_all_evidence_view(request):
    reference = get_reference(request)
    evidences = DBSession.query(Evidence).options(joinedload('bioent_biocon_evidences'), joinedload('bioent_biocon_evidences.bioent_biocon'), joinedload('bioent_biocon_evidences.bioent_biocon.bioentity'), joinedload('bioent_biocon_evidences.bioent_biocon.bioconcept')).filter(Evidence.reference_id==reference.id).all()
    tables = {}
    tables['phenotype'] = get_phenotypes(evidences)
    tables['chemical_phenotype'] = get_chemical_phenotypes(evidences)
    tables['pp_rna_phenotype'] = get_pp_rna_phenotypes(evidences)
    tables['go'] = get_gos(evidences)
    tables['interaction'] = get_interactions(evidences)

    return tables

#-------GO Information------
def get_gos(evidences):
    goevidences = [evidence for evidence in evidences if evidence.evidence_type == 'GO_EVIDENCE']
    evidence_map = dict([(evidence.id, evidence.bioent_biocon) for evidence in goevidences])
    
    def f(evidences, group_term, bioent_biocon):
        total_entry = entry_with_link(str(len(evidences)), bioent_biocon.link)
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, total_entry]
    return create_grouped_evidence_table(goevidences, evidence_map, f)

#-------Phenotype Information------
# Main phenotype information
def get_phenotypes(evidences):
    phenoevidences = [evidence for evidence in evidences if evidence.evidence_type == 'PHENOTYPE_EVIDENCE' and evidence.bioent_biocon.bioconcept.name not in pp_rna_phenotypes and evidence.bioent_biocon.bioconcept.name not in chemical_phenotypes]
    evidence_map = dict([(evidence.id, evidence.bioent_biocon) for evidence in phenoevidences])
    
    def f(evs_for_group, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evs_for_group]
        total_entry = entry_with_note(entry_with_link(str(len(evs_for_group)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, total_entry]
    return create_grouped_evidence_table(phenoevidences, evidence_map, f)

# Chemical Phenotype Information
def get_chemical_phenotypes(evidences):
    phenoevidences = [evidence for evidence in evidences if evidence.evidence_type == 'PHENOTYPE_EVIDENCE' and evidence.bioent_biocon.bioconcept.name in chemical_phenotypes]
    evidence_map = dict([(evidence.id, (evidence.bioent_biocon,  ', '.join([chem.name for chem in evidence.chemicals]))) for evidence in phenoevidences])
    
    def f(evidences, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evidences]
        total_entry = entry_with_note(entry_with_link(str(len(evidences)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, group_term[1], total_entry]
    return create_grouped_evidence_table(phenoevidences, evidence_map, f)

# Protein/peptide and RNA Phenotype Information
def get_pp_rna_phenotypes(evidences):
    phenoevidences = [evidence for evidence in evidences if evidence.evidence_type == 'PHENOTYPE_EVIDENCE' and evidence.bioent_biocon.bioconcept.name in pp_rna_phenotypes]
    evidence_map = dict([(evidence.id, (evidence.bioent_biocon, evidence.reporter)) for evidence in phenoevidences])
    
    def f(evidences, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evidences]
        total_entry = entry_with_note(entry_with_link(str(len(evidences)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, group_term[1], total_entry]
    return create_grouped_evidence_table(phenoevidences, evidence_map, f)

#-------Interaction Information------
def get_interactions(evidences):
    interevidences = [evidence for evidence in evidences if evidence.evidence_type == 'INTERACTION_EVIDENCE']
    evidence_map = dict([(evidence.id, evidence.biorel.id) for evidence in interevidences])
    
    def f(evidences, group_term, biorel):
        endpoint1_entry = biorel.source_bioent.name_with_link
        endpoint2_entry = biorel.sink_bioent.name_with_link
        total_entry = entry_with_link(str(len(evidences)), biorel.link)
        return [endpoint1_entry, endpoint2_entry, total_entry]
        
    return create_grouped_evidence_table(interevidences, evidence_map, f)
