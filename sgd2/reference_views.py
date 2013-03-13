'''
Created on Feb 21, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Goevidence, Phenoevidence, \
    Interevidence
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
    go_evidences = DBSession.query(Goevidence).options(joinedload('bioent_biocon'), joinedload('bioent_biocon.bioentity'), joinedload('bioent_biocon.bioconcept')).filter(Goevidence.reference_id==reference.id).all()
    pheno_evidences = DBSession.query(Phenoevidence).options(joinedload('bioent_biocon'), joinedload('bioent_biocon.bioentity'), joinedload('bioent_biocon.bioconcept')).filter(Phenoevidence.reference_id==reference.id).all()
    
    inter_evidences = DBSession.query(Interevidence).options(joinedload('biorel')).filter(Interevidence.reference_id==reference.id).all()

    tables = {}
    tables['phenotype'] = get_phenotypes(pheno_evidences)
    tables['chemical_phenotype'] = get_chemical_phenotypes(pheno_evidences)
    tables['pp_rna_phenotype'] = get_pp_rna_phenotypes(pheno_evidences)
    tables['go'] = get_gos(go_evidences)
    tables['interaction'] = get_interactions(inter_evidences)

    return tables

#-------GO Information------
@view_config(route_name='reference_go', renderer="json")
def reference_go_view(request):
    reference = get_reference(request)
    go_evidences = DBSession.query(Goevidence).options(joinedload('bioent_biocon'), joinedload('bioent_biocon.bioentity'), joinedload('bioent_biocon.bioconcept')).filter(Goevidence.reference_id==reference.id).all()
    
    return {"aaData": get_gos(go_evidences)}

def get_gos(evidences):
    evidence_map = dict([(evidence.id, evidence.bioent_biocon) for evidence in evidences])
    
    def f(evidences, group_term, bioent_biocon):
        total_entry = entry_with_link(str(len(evidences)), bioent_biocon.link)
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, total_entry]
    return create_grouped_evidence_table(evidences, evidence_map, f)

#-------Phenotype Information------
@view_config(route_name='reference_phenotype', renderer="json")
def reference_phenotype(request):
    reference = get_reference(request)
    pheno_evidences = DBSession.query(Phenoevidence).options(joinedload('bioent_biocon'), joinedload('bioent_biocon.bioentity'), joinedload('bioent_biocon.bioconcept')).filter(Phenoevidence.reference_id==reference.id).all()
    
    tables = {}
    tables['phenotype'] = get_phenotypes(pheno_evidences)
    tables['chemical_phenotype'] = get_chemical_phenotypes(pheno_evidences)
    tables['pp_rna_phenotype'] = get_pp_rna_phenotypes(pheno_evidences)

    return tables

# Main phenotype information
def get_phenotypes(evidences):
    phenoevidences = [evidence for evidence in evidences 
                      if evidence.bioent_biocon.bioconcept.name not in pp_rna_phenotypes and evidence.bioent_biocon.bioconcept.name not in chemical_phenotypes]
    evidence_map = dict([(evidence.id, evidence.bioent_biocon) for evidence in phenoevidences])
    
    def f(evs_for_group, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evs_for_group]
        total_entry = entry_with_note(entry_with_link(str(len(evs_for_group)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, total_entry]
    return create_grouped_evidence_table(phenoevidences, evidence_map, f)

# Chemical Phenotype Information
def get_chemical_phenotypes(evidences):
    phenoevidences = [evidence for evidence in evidences 
                      if evidence.bioent_biocon.bioconcept.name in chemical_phenotypes]
    evidence_map = dict([(evidence.id, (evidence.bioent_biocon,  ', '.join([chem.name for chem in evidence.chemicals]))) for evidence in phenoevidences])
    
    def f(evidences, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evidences]
        total_entry = entry_with_note(entry_with_link(str(len(evidences)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, group_term[1], total_entry]
    return create_grouped_evidence_table(phenoevidences, evidence_map, f)

# Protein/peptide and RNA Phenotype Information
def get_pp_rna_phenotypes(evidences):
    phenoevidences = [evidence for evidence in evidences 
                      if evidence.bioent_biocon.bioconcept.name in pp_rna_phenotypes]
    evidence_map = dict([(evidence.id, (evidence.bioent_biocon, evidence.reporter)) for evidence in phenoevidences])
    
    def f(evidences, group_term, bioent_biocon):
        quals = [evidence.qualifier for evidence in evidences]
        total_entry = entry_with_note(entry_with_link(str(len(evidences)), bioent_biocon.link), create_phenotype_note(quals))
        return [bioent_biocon.bioconcept.name_with_link, bioent_biocon.bioentity.name_with_link, group_term[1], total_entry]
    return create_grouped_evidence_table(phenoevidences, evidence_map, f)

#-------Interaction Information------
@view_config(route_name='reference_interaction', renderer="json")
def reference_interaction_view(request):
    reference = get_reference(request)
    inter_evidences = DBSession.query(Interevidence).options(joinedload('biorel')).filter(Interevidence.reference_id==reference.id).all()

    return {"aaData": get_interactions(inter_evidences)}

def get_interactions(evidences):
    evidence_map = dict([(evidence.id, evidence.biorel.id) for evidence in evidences])
    
    def f(evidences, group_term, biorel):
        endpoint1_entry = biorel.source_bioent.name_with_link
        endpoint2_entry = biorel.sink_bioent.name_with_link
        total_entry = entry_with_link(str(len(evidences)), biorel.link)
        return [endpoint1_entry, endpoint2_entry, total_entry]
        
    return create_grouped_evidence_table(evidences, evidence_map, f)
