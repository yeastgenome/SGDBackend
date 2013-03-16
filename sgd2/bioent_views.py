'''
Created on Feb 20, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import BioentBiocon
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Goevidence, Phenoevidence
from pyramid.view import view_config
from sgd2.biocon_views import make_go_table
from sgd2.models import DBSession
from sgd2.views import site_layout
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload
from utils.graph import create_interaction_graph, create_go_graph
from utils.utils import create_grouped_evidence_table, entry_with_link

pp_rna_phenotypes = set(['protein-peptide accumulation', 'protein-peptide distribution', 'protein-peptide modification', 'RNA accumulation', 'RNA localization', 'RNA modification'])
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
    go_bioent_biocons = DBSession.query(BioentBiocon).filter(BioentBiocon.bioent_id==bioent.id).filter(BioentBiocon.biocon_type=='GO').all()
    go_bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in go_bioent_biocons]
    pheno_bioent_biocons = DBSession.query(BioentBiocon).filter(BioentBiocon.bioent_id==bioent.id).filter(BioentBiocon.biocon_type=='PHENOTYPE').all()
    pheno_bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in pheno_bioent_biocons]
    
    goevidences = DBSession.query(Goevidence).options(joinedload('bioent_biocon'), joinedload('reference'), joinedload('bioent_biocon.bioconcept')).filter(Goevidence.bioent_biocon_id.in_(go_bioent_biocon_ids)).all()
    phenoevidences = DBSession.query(Phenoevidence).options(joinedload('bioent_biocon'), joinedload('reference'), joinedload('bioent_biocon.bioconcept')).filter(Phenoevidence.bioent_biocon_id.in_(pheno_bioent_biocon_ids)).all()
    
    tables = {}
    tables['phenotype'] = get_phenotypes(phenoevidences)
    tables['chemical_phenotype'] = get_chemical_phenotypes(phenoevidences)
    tables['pp_rna_phenotype'] = get_pp_rna_phenotypes(phenoevidences)
    
    tables.update(make_go_table(goevidences, False))

    return tables

#-------GO Information------
@view_config(route_name='bioent_go', renderer="json")
def bioent_go_view(request):
    bioent = get_bioent(request)
    go_bioent_biocons = DBSession.query(BioentBiocon).filter(BioentBiocon.bioent_id==bioent.id).filter(BioentBiocon.biocon_type=='GO').all()
    go_bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in go_bioent_biocons]

    goevidences = DBSession.query(Goevidence).options(joinedload('bioent_biocon'), joinedload('reference'), joinedload('bioent_biocon.bioconcept')).filter(Goevidence.bioent_biocon_id.in_(go_bioent_biocon_ids)).all()
    
    return make_go_table(goevidences, False)


#-------Phenotype Information------
@view_config(route_name='bioent_phenotype', renderer="json")
def bioent_phenotype_view(request):
    bioent = get_bioent(request)
    pheno_bioent_biocons = DBSession.query(BioentBiocon).filter(BioentBiocon.bioent_id==bioent.id).filter(BioentBiocon.biocon_type=='PHENOTYPE').all()
    pheno_bioent_biocon_ids = [bioent_biocon.id for bioent_biocon in pheno_bioent_biocons]
    
    phenoevidences = DBSession.query(Phenoevidence).options(joinedload('bioent_biocon'), joinedload('reference'), joinedload('bioent_biocon.bioconcept')).filter(Phenoevidence.bioent_biocon_id.in_(pheno_bioent_biocon_ids)).all()
     
    tables = {}
    tables['phenotype'] = get_phenotypes(phenoevidences)
    tables['chemical_phenotype'] = get_chemical_phenotypes(phenoevidences)
    tables['pp_rna_phenotype'] = get_pp_rna_phenotypes(phenoevidences)

    return tables

# Main phenotype information
def get_phenotypes(evidences):
    other_phenotypes = set()
    other_phenotypes.update(chemical_phenotypes)
    other_phenotypes.update(pp_rna_phenotypes)
    pheno_evidences = [evidence for evidence in evidences 
                if evidence.bioent_biocon.bioconcept.name not in other_phenotypes]
    evidence_map = dict([(evidence.id, (evidence.bioent_biocon, evidence.qualifier, evidence.mutant_type)) for evidence in pheno_evidences])
    
    def f(evs_for_group, group_term, bioent_biocon):
        return [bioent_biocon.bioconcept.name_with_link, group_term[1], group_term[2]]
        
    return create_grouped_evidence_table(pheno_evidences, evidence_map, f)

# Chemical Phenotype Information
def get_chemical_phenotypes(evidences):
    chem_evidences = [evidence for evidence in evidences 
                 if evidence.bioent_biocon.bioconcept.name in chemical_phenotypes]
    evidence_map = dict([(evidence.id, (', '.join([chem.name for chem in evidence.chemicals]), evidence.bioent_biocon, evidence.qualifier, evidence.mutant_type)) for evidence in chem_evidences])
    
    def f(evs_for_group, group_term, bioent_biocon):
        return [bioent_biocon.bioconcept.name_with_link, group_term[0], group_term[2], group_term[3]]
    
    return create_grouped_evidence_table(chem_evidences, evidence_map, f)

# Protein/peptide and RNA Phenotype Information
def get_pp_rna_phenotypes(evidences):
    pp_rna_evidences = [evidence for evidence in evidences 
                 if evidence.bioent_biocon.bioconcept.name in pp_rna_phenotypes]
    evidence_map = dict([(evidence.id, (evidence.reporter, evidence.bioent_biocon, evidence.qualifier, evidence.mutant_type)) for evidence in pp_rna_evidences])
    
    def f(evs_for_group, group_term, bioent_biocon):
        return [bioent_biocon.bioconcept.name_with_link, group_term[0], group_term[2], group_term[3]]
    
    return create_grouped_evidence_table(pp_rna_evidences, evidence_map, f)

#------------------Biorel Information-----------------------
@view_config(route_name='bioent_all_biorel', renderer="json")
def bioent_all_biorel_view(request):
    bioent = get_bioent(request)
    
    tables = {}
    tables['interaction'] = get_interactions(bioent)
    return tables

#-------Interaction Information------
@view_config(route_name='bioent_interaction', renderer="json")
def bioent_interaction_view(request):
    bioent = get_bioent(request)
    
    return {"aaData":get_interactions(bioent)}

def get_interactions(bioent):
    interactions = [interaction for interaction in bioent.biorelations if interaction.biorel_type == 'INTERACTION']
    
    table = []
    for biorel in interactions:     
        biorel_entry = biorel.get_opposite(bioent).name_with_link
        total_entry = entry_with_link(str(biorel.evidence_count), biorel.link)
        table.append([biorel_entry, str(biorel.genetic_evidence_count), str(biorel.physical_evidence_count), total_entry])
    return table

#Cytoscape graph
@view_config(route_name='bioent_interaction_graph', renderer="json")
def bioent_interaction_graph_view(request):
    try:
        bioent = get_bioent(request)
        graph = create_interaction_graph(bioent)
        return graph
    except DBAPIError:
        return ['Error']
    
@view_config(route_name='bioent_go_graph', renderer="json")
def bioent_go_graph_view(request):
    try:
        bioent = get_bioent(request)
        graph = create_go_graph(bioent)
        return graph
    except DBAPIError:
        return ['Error']


