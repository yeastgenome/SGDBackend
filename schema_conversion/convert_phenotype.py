'''
Created on May 6, 2013

@author: kpaskov
'''
from schema_conversion import cache, create_or_update, \
    create_or_update_and_remove, add_or_check
from schema_conversion.output_manager import OutputCreator

id_to_bioent = {}
observable_to_phenotype = {}
name_to_chemical = {}
id_to_evidence = {}
tuple_to_bioent_biocon = {}
tuple_to_reflink = {}
name_to_allele = {}
tuple_to_phenoevidence_chemical = {}

def create_bioent_biocon_name(bioent, biocon):
    return bioent.official_name + '---' + biocon.official_name


"""
------------Phenotype--------------
"""

def create_phenotype_id(observable):
    return observable_to_phenotype[observable].id

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
                                 biocon_id=old_phenotype.id, date_created=old_phenotype.date_created, created_by=old_phenotype.created_by)
    return new_phenotype

def create_bioent_biocon(old_phenotype_feature):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    bioent_id = old_phenotype_feature.feature_id
    biocon_observable = old_phenotype_feature.observable
        
    if bioent_id in id_to_bioent and biocon_observable in observable_to_phenotype:
        bioent = id_to_bioent[bioent_id]
        biocon = observable_to_phenotype[biocon_observable]
        name = create_bioent_biocon_name(bioent, biocon)
        return NewBioentBiocon(bioent_id, biocon.id, name, biocon.biocon_type)
    else:
        return None

def create_allele(old_phenotype_feature):
    from model_new_schema.evidence import Allele as NewAllele
    if old_phenotype_feature.experiment is not None:
        allele_info = old_phenotype_feature.experiment.allele
        if allele_info is not None:
            new_allele = NewAllele(allele_info[0], allele_info[1])
            return new_allele
    return None

def create_phenoevidence(old_phenotype_feature):
    from model_new_schema.evidence import Phenoevidence as NewPhenoevidence
    evidence_id = create_phenoevidence_id(old_phenotype_feature.id)
    reference_id = tuple_to_reflink[('PHENO_ANNOTATION_NO', old_phenotype_feature.id)].reference_id
    strain_id = None
    allele_id = None
    bioent_id = old_phenotype_feature.feature_id
    biocon_id = create_phenotype_id(old_phenotype_feature.observable)
    if (bioent_id, biocon_id, 'PHENOTYPE') in tuple_to_bioent_biocon:
        bioent_biocon_id = tuple_to_bioent_biocon[(bioent_id, biocon_id, 'PHENOTYPE')].id
    else:
        bioent_biocon_id = None

    new_phenoevidence = NewPhenoevidence(old_phenotype_feature.experiment_type, reference_id, strain_id, old_phenotype_feature.mutant_type, 
                                         allele_id, old_phenotype_feature.source, old_phenotype_feature.qualifier, bioent_biocon_id,
                                         session=None, evidence_id=evidence_id, date_created=old_phenotype_feature.date_created, created_by=old_phenotype_feature.created_by)
    if old_phenotype_feature.experiment is not None:
        experiment = old_phenotype_feature.experiment
        new_phenoevidence.reporter = None if experiment.reporter == None else experiment.reporter[0]
        new_phenoevidence.reporter_desc = None if experiment.reporter == None else experiment.reporter[1]
        new_phenoevidence.strain_id = None if experiment.strain == None else experiment.strain[0]
        new_phenoevidence.strain_details = None if experiment.strain == None else experiment.strain[1]
        new_phenoevidence.budding_index = None if experiment.budding_index == None else float(experiment.budding_index)
        new_phenoevidence.glutathione_excretion = None if experiment.glutathione_excretion == None else float(experiment.glutathione_excretion)
        new_phenoevidence.z_score = experiment.z_score
        new_phenoevidence.relative_fitness_score = None if experiment.relative_fitness_score == None else float(experiment.relative_fitness_score)
        new_phenoevidence.chitin_level = None if experiment.chitin_level == None else float(experiment.chitin_level)
    
        comment = experiment.experiment_comment
        if comment is not None:
            new_phenoevidence.experiment_details = comment
            
        if len(experiment.condition) > 0:
            conditions = []
            for (a, b) in experiment.condition:
                if b is None:
                    conditions.append(a)
                else:
                    conditions.append(a + '- ' + b)
            condition_info = ', '.join(conditions)
            new_phenoevidence.conditions = condition_info
            
        if len(experiment.details) > 0:
            details = []
            for (a, b) in experiment.details:
                if b is None:
                    details.append(a)
                else:
                    details.append(a + '- ' + b)
            detail_info = ', '.join(details)
            new_phenoevidence.details = detail_info
            
    return new_phenoevidence  

def add_allele(old_phenotype_feature):
    evidence_id = create_phenoevidence_id(old_phenotype_feature.id)
    evidence = id_to_evidence[evidence_id]
    
    if old_phenotype_feature.experiment is not None:
        allele_info = old_phenotype_feature.experiment.allele
        if allele_info is not None:
            allele_name = allele_info[0]
            evidence.mutant_allele_id = name_to_allele[allele_name].id
    return evidence

def create_chemical(chemical_info):
    from model_new_schema.chemical import Chemical as NewChemical
    new_chemical = NewChemical(chemical_info[0][0])
    return new_chemical

def create_phenoevidence_chemical(chemical):
    from model_new_schema.evidence import PhenoevidenceChemical as NewPhenoevidenceChemical
    evidence_id = create_phenoevidence_id(chemical[1].id)
    chemical_info = chemical[0]
    chemical_id = name_to_chemical[chemical_info[0]].id
    chemical_amount = chemical_info[1]
    new_pheno_chemical = NewPhenoevidenceChemical(evidence_id, chemical_id, chemical_amount)
    return new_pheno_chemical

     
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
    from model_old_schema.reference import Reflink as OldReflink
    from model_old_schema.cv import CVTerm as OldCVTerm
    

#    #Cache bioents
#    bioent_oc = OutputCreator('bioent')
#    cache(NewBioentity, id_to_bioent, lambda x: x.id, new_session, bioent_oc)
# 
#    #Cache phenotypes
#    phenotype_oc = OutputCreator('phenotype')
#    cache(NewPhenotype, observable_to_phenotype, lambda x: x.observable, new_session, phenotype_oc)
#
#    #Create new phenotypes if they don't exist, or update the database if they do.
#    old_phenotypes = old_session.query(OldPhenotype).all()
#    key_maker = lambda x: x.observable
#    values_to_check = ['observable', 'phenotype_type']
#    create_or_update_and_remove(old_phenotypes, observable_to_phenotype, create_phenotype, key_maker, values_to_check, new_session, phenotype_oc)
#
#    #Add definitions to phenotypes
#    phenotype_output_creator = OutputCreator('phenotype')
#    #Cache phenotypes
#    cache(NewPhenotype, observable_to_phenotype, lambda x: x.observable, new_session, phenotype_output_creator)
#    cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==6).all()
#    for cv_term in cv_terms:
#        new_phenotype = NewPhenotype(cv_term.name, create_phenotype_type(cv_term.name), cv_term.definition)
#        values_to_check = ['observable', 'phenotype_type', 
#                           'biocon_type', 'official_name', 'description']
#        add_or_check(new_phenotype, observable_to_phenotype, new_phenotype.observable, values_to_check, new_session, phenotype_output_creator)
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
#    #Cache reflinks
#    output_creator_reflink = OutputCreator('reflink')
#    cache(OldReflink, tuple_to_reflink, lambda x: (x.col_name, x.primary_key), old_session, output_creator_reflink)
#    
#    #Cache phenoevidences
#    output_creator_phenoevidence = OutputCreator('phenoevidence')
#    cache(NewPhenoevidence, id_to_evidence, lambda x: x.id, new_session, output_creator_phenoevidence)
#
#    #Create new phenoevidences if they don't exist, or update the database if they do.
#    key_maker = lambda x: x.id
#    values_to_check = ['mutant_type', 'source', 'qualifier', 'reporter', 'reporter_desc', 'strain_details', 
#                       'budding_index', 'glutathione_excretion', 'z_score', 'relative_fitness_score', 'chitin_level', 'description', 'bioent_biocon_id',
#                       'conditions', 'details', 'experiment_details',
#                       'experiment_type', 'reference_id', 'evidence_type', 'strain_id', 'source', 'date_created', 'created_by']
#    create_or_update_and_remove(old_phenotype_features, id_to_evidence, create_phenoevidence, key_maker, values_to_check, new_session, output_creator_phenoevidence)
#
#    #Cache alleles
#    output_creator_allele = OutputCreator('allele')
#    cache(NewAllele, name_to_allele, lambda x: x.official_name, new_session, output_creator_allele)
#    
#    #Create new alleles if they don't exist, or update the database if they do.
#    values_to_check = ['parent_id', 'more_info']
#    create_or_update_and_remove(old_phenotype_features, name_to_allele, create_allele, lambda x: x.official_name, values_to_check, new_session, output_creator_allele)
#
#    new_session.commit()
#    values_to_check = ['mutant_allele_id']
#    create_or_update(old_phenotype_features, id_to_evidence, add_allele, lambda x: x.id, values_to_check, new_session, output_creator_phenoevidence)

#    #Cache chemicals
#    key_maker = lambda x: x.name
#    output_creator_chemical = OutputCreator('chemical')
#    cache(NewChemical, name_to_chemical, key_maker, new_session, output_creator_chemical)
#    
#    #Create new chemicals if they don't exist, or update the database if they do.
#    values_to_check = ['name']
#    chemical_infos = []
#    for old_phenotype_feature in old_phenotype_features:
#        if old_phenotype_feature.experiment != None:
#            more_chemicals = old_phenotype_feature.experiment.chemicals
#            chemical_infos.extend([(x, old_phenotype_feature) for x in more_chemicals])
#
#    create_or_update_and_remove(chemical_infos, name_to_chemical, create_chemical, key_maker, values_to_check, new_session, output_creator_chemical)
#
#    #Cache evidence_chemical
#    key_maker = lambda x: (x.evidence_id, x.chemical_id)
#    output_creator_chemical = OutputCreator('evidence_chemical')
#    cache(NewPhenoevidenceChemical, tuple_to_phenoevidence_chemical, key_maker, new_session, output_creator_chemical)
#    
#    #Create new evidence_chemical if they don't exist, or update the database if they do.
#    values_to_check = ['evidence_id', 'chemical_id', 'chemical_amt']
#    create_or_update_and_remove(chemical_infos, tuple_to_phenoevidence_chemical, create_phenoevidence_chemical, key_maker, values_to_check, 
#                    new_session, output_creator_chemical)
    
    #Add phenotype ontology
    for cv_term in cv_terms:
        child_id = name_to_phenotype[cv_term.name].id
        for parent in cv_term.parents:
            parent_id = name_to_phenotype[parent.name].id
            
            biocon_biocon = NewBioconBiocon(parent_id, child_id, 'is a')
            new_session.add(biocon_biocon)
        
        parents = list(cv_term.parents)
        while len(parents) > 0:
            parent = parents.pop()
            biocon_ancestor = NewBioconAncestor(name_to_phenotype[parent.name].id, child_id)
            new_session.add(biocon_ancestor)
            parents.extend(parent.parents)
        
        
            
    
