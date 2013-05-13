'''
Created on May 6, 2013

@author: kpaskov
'''
from schema_conversion import cache, create_or_update, \
    create_or_update_and_remove, add_or_check
from schema_conversion.output_manager import OutputCreator

id_to_bioent = {}
id_to_phenotype = {}
name_to_chemical = {}
id_to_evidence = {}
tuple_to_bioent_biocon = {}

def create_bioent_biocon_name(bioent, biocon):
    return bioent.official_name + '---' + biocon.official_name


"""
------------Phenotype--------------
"""

def create_phenotype_id(old_phenotype_id):
    return old_phenotype_id

def create_phenoevidence_id(old_evidence_id):
    return old_evidence_id

def create_phenotype_type(observable):
    if observable in {'chemical compound accumulation', 'resistance to chemicals', 'osmotic stress resistance', 'alkaline pH resistance',
                      'ionic stress resistance', 'oxidative stress resistance', 'small molecule transport', 'metal resistance', 
                      'acid pH resistance', 'hyperosmotic stress resistance', 'hypoosmotic stress resistance', 'chemical compound excretion'}:
        return 'chemical'
    elif observable in {'protein/peptide accumulation', 'protein/peptide modification', 'protein/peptide distribution', 
                        'RNA accumulation', 'RNA localization', 'RNA modification'}:
        return 'pp_rna'
    else:
        return 'cellular'

def create_phenotype(old_phenotype):
    from model_new_schema.bioconcept import Phenotype as NewPhenotype
    new_phenotype = NewPhenotype(old_phenotype.observable, create_phenotype_type(old_phenotype.observable), None, 
                                 biocon_id=create_phenotype_id(old_phenotype.id), date_created=old_phenotype.date_created, created_by=old_phenotype.created_by)
    return new_phenotype

def create_bioent_biocon(old_phenotype_feature):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    bioent_id = old_phenotype_feature.feature_id
    biocon_id = create_phenotype_id(old_phenotype_feature.phenotype_id)
        
    if bioent_id in id_to_bioent and biocon_id in id_to_phenotype:
        bioent = id_to_bioent[bioent_id]
        biocon = id_to_phenotype[biocon_id]
        name = create_bioent_biocon_name(bioent, biocon)
        return NewBioentBiocon(bioent_id, biocon_id, name, biocon.biocon_type)
    else:
        return None

def create_allele(old_phenotype_feature):
    from model_new_schema.evidence import Allele as NewAllele
    allele_info = old_phenotype_feature.experiment.allele
    new_allele = NewAllele(allele_info[0], allele_info[1])
    return new_allele

def create_chemical(old_phenotye_feature):
    from model_new_schema.chemical import Chemical as NewChemical
    chemical_info = old_phenotye_feature.experiment.chemical
    new_chemical = NewChemical(chemical_info[0])
    return new_chemical

def create_phenoevidence(old_phenotye_feature):
    from model_new_schema.evidence import Phenoevidence as NewPhenoevidence
    evidence_id = create_phenoevidence_id(old_phenotye_feature.id)
    reference_id = None
    strain_id = None
    allele_id = None
    new_phenoevidence = NewPhenoevidence(old_phenotye_feature.experiment_type, reference_id, strain_id, old_phenotye_feature.mutant_type, 
                                         allele_id, old_phenotye_feature.source, old_phenotye_feature.qualifier, 
                                         session=None, evidence_id=create_phenoevidence_id(evidence_id), date_created=old_phenotye_feature.date_created, created_by=old_phenotye_feature.created_by)
    if old_phenotye_feature.experiment is not None:
        experiment = old_phenotye_feature.experiment
        new_phenoevidence.reporter = None if experiment.reporter == None else experiment.reporter[0]
        new_phenoevidence.reporter_desc = None if experiment.reporter == None else experiment.reporter[1]
        new_phenoevidence.strain_id = None if experiment.strain == None else experiment.strain[0]
        new_phenoevidence.strain_details = None if experiment.strain == None else experiment.strain[1]
        new_phenoevidence.budding_index = None if experiment.budding_index == None else experiment.budding_index
        new_phenoevidence.glutathione_excretion = experiment.glutathione_excretion
        new_phenoevidence.z_score = experiment.z_score
        new_phenoevidence.relative_fitness_score = experiment.relative_fitness_score
        new_phenoevidence.chitin_level = experiment.chitin_level
    
        description_pieces = []
        comment = experiment.experiment_comment
        if comment is not None:
            description_pieces.append('Experiment: ' + comment)
            
        if len(experiment.condition) > 0:
            conditions = []
            for (a, b) in experiment.condition:
                if b is None:
                    conditions.append(a)
                else:
                    conditions.append(a + '- ' + b)
            condition_info = ', '.join(conditions)
            description_pieces.append('Condition: ' + condition_info)
            
        if len(experiment.details) > 0:
            details = []
            for (a, b) in experiment.details:
                if b is None:
                    details.append(a)
                else:
                    details.append(a + '- ' + b)
            detail_info = ', '.join(details)
            description_pieces.append('Details: ' + detail_info)
            
        new_phenoevidence.description = '; '.join(description_pieces)

    return new_phenoevidence    

def create_phenoevidence_chemical(old_phenotype_feature):
    from model_new_schema.evidence import PhenoevidenceChemical as NewPhenoevidenceChemical
    evidence_id = create_phenoevidence_id(old_phenotype_feature.id)
    chemical_info = old_phenotype_feature.experiment.chemical
    if chemical_info is not None:
        chemical_id = name_to_chemical[chemical_info[0]]
        chemical_amount = chemical_info[1]
        new_pheno_chemical = NewPhenoevidenceChemical(evidence_id, chemical_id, chemical_amount)
        return new_pheno_chemical
    return None

     
"""
---------------------Convert------------------------------
"""  

def convert_phenotype(old_session, new_session):
    from model_new_schema.evidence import Allele as NewAllele, PhenoevidenceChemical as NewPhenoevidenceChemical, Phenoevidence as NewPhenoevidence
    from model_new_schema.chemical import Chemical as NewChemical
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.bioconcept import Phenotype as NewPhenotype, BioconBiocon as NewBioconBiocon, BioconAncestor as NewBioconAncestor, \
        BioentBiocon as NewBioentBiocon

    from model_old_schema.phenotype import PhenotypeFeature as OldPhenotypeFeature, Phenotype as OldPhenotype
    from model_old_schema.cv import CVTerm as OldCVTerm
    

#    #Cache bioents
#    bioent_oc = OutputCreator('bioent')
#    cache(NewBioentity, id_to_bioent, lambda x: x.id, new_session, bioent_oc)
# 
#    #Cache phenotypes
#    phenotype_oc = OutputCreator('phenotype')
#    cache(NewPhenotype, id_to_phenotype, lambda x: x.observable, new_session, phenotype_oc)
#
#    #Create new phenotypes if they don't exist, or update the database if they do.
#    old_phenotypes = old_session.query(OldPhenotype).all()
#    key_maker = lambda x: x.observable
#    values_to_check = ['observable', 'phenotype_type']
#    create_or_update_and_remove(old_phenotypes, id_to_phenotype, create_phenotype, key_maker, values_to_check, new_session, phenotype_oc)
#
#    #Add definitions to phenotypes
#    phenotype_output_creator = OutputCreator('phenotype')
#    #Cache phenotypes
#    cache(NewPhenotype, id_to_phenotype, lambda x: x.observable, new_session, phenotype_output_creator)
#    cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==6).all()
#    for cv_term in cv_terms:
#        new_phenotype = NewPhenotype(cv_term.name, create_phenotype_type(cv_term.name), cv_term.definition)
#        values_to_check = ['observable', 'phenotype_type', 
#                           'biocon_type', 'official_name', 'description']
#        add_or_check(new_phenotype, id_to_phenotype, new_phenotype.observable, values_to_check, new_session, phenotype_output_creator)
#    phenotype_output_creator.finished()   
#
#    #Cache bioent_biocons
#    bioent_biocon_oc = OutputCreator('bioent_biocon')
#    key_maker = lambda x: (x.bioent_id, x.biocon_id, x.biocon_type)
#    cache(NewBioentBiocon, tuple_to_bioent_biocon, lambda x: (x.bioent_id, x.biocon_id, x.biocon_type), new_session, bioent_biocon_oc)
#    
#    #Create new bioent_biocons if they don't exist, or update the database if they do.
    old_phenotype_features = old_session.query(OldPhenotypeFeature).all()
#    values_to_check = ['bioent_id', 'biocon_id', 'official_name', 'biocon_type']
#    create_or_update(old_phenotype_features, tuple_to_bioent_biocon, create_bioent_biocon, key_maker, values_to_check, new_session, bioent_biocon_oc)
#    
    #Cache phenoevidences
    output_creator = OutputCreator('phenoevidence')
    cache(NewPhenoevidence, id_to_evidence, lambda x: x.id, new_session, output_creator)

    #Create new phenoevidences if they don't exist, or update the database if they do.
    key_maker = lambda x: x.id
    values_to_check = ['mutant_type', 'mutant_allele_id', 'source', 'qualifier', 'reporter', 'reporter_desc', 'strain_details', 
                       'budding_index', 'glutathione_excretion', 'z_score', 'relative_fitness_score', 'chitin_level', 'description']
    create_or_update_and_remove(old_phenotype_features, id_to_evidence, create_phenoevidence, key_maker, values_to_check, new_session, output_creator)

#    #Cache alleles
#    key_maker = lambda x: x.name
#    output_message = 'allele'
#    cache(NewAllele, name_to_allele, key_maker, session, output_creator, output_message)
#    
#    #Create new alleles if they don't exist, or update the database if they do.
#    values_to_check = ['name', 'description']
#    create_or_update(old_phenotype_features, name_to_allele, create_allele, key_maker, values_to_check, old_model, output_creator, output_message)
#
#    #Cache chemicals
#    key_maker = lambda x: x.name
#    output_message = 'chemical'
#    cache(NewChemical, name_to_chemical, key_maker, session, output_creator, output_message)
#    
#    #Create new chemicals if they don't exist, or update the database if they do.
#    values_to_check = ['name', 'description']
#    create_or_update(old_phenotype_features, name_to_allele, create_allele, key_maker, values_to_check, old_model, output_creator, output_message)
#
#    #Cache evidence_chemical
#    key_maker = lambda x: (x.evidence_id, x.chemical_id)
#    output_message = 'evidence_chemical'
#    cache(NewPhenoevidenceChemical, tuple_to_phenoevidence_chemical, key_maker, session, output_creator, output_message)
#    
#    #Create new evidence_chemical if they don't exist, or update the database if they do.
#    values_to_check = ['evidence_id', 'chemical_id', 'chemical_amt']
#    create_or_update(old_phenotype_features, tuple_to_phenoevidence_chemical, create_phenoevidence_chemical, key_maker, values_to_check, 
#                     old_model, output_creator, output_message)
    
#    #Add phenotype ontology
#    for cv_term in cv_terms:
#        child_id = name_to_phenotype[cv_term.name].id
#        for parent in cv_term.parents:
#            parent_id = name_to_phenotype[parent.name].id
#            
#            biocon_biocon = NewBioconBiocon(parent_id, child_id, 'is a')
#            new_session.add(biocon_biocon)
#        
#        parents = list(cv_term.parents)
#        while len(parents) > 0:
#            parent = parents.pop()
#            biocon_ancestor = NewBioconAncestor(name_to_phenotype[parent.name].id, child_id)
#            new_session.add(biocon_ancestor)
#            parents.extend(parent.parents)
        
        
            
    
