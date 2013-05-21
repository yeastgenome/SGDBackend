'''
Created on May 6, 2013

@author: kpaskov
'''
from schema_conversion import cache, create_or_update_and_remove, ask_to_commit
import datetime


def create_bioent_biocon_name(bioent, biocon):
    return bioent.official_name + '---' + biocon.official_name


"""
------------Phenotype--------------
"""

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
    
def create_phenotype_key(observable):
    name = observable.replace(' ', '_')
    name = name.replace('/', '-')
    return (name, 'PHENOTYPE')

def create_phenotype(old_phenotype):
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    new_phenotype = NewPhenotype(old_phenotype.id, old_phenotype.observable, create_phenotype_type(old_phenotype.observable), None,
                                 old_phenotype.date_created, old_phenotype.created_by)
    return new_phenotype

def create_allele(old_phenotype_feature):
    from model_new_schema.misc import Allele as NewAllele
    if old_phenotype_feature.experiment is not None:
        allele_info = old_phenotype_feature.experiment.allele
        if allele_info is not None:
            new_allele = NewAllele(allele_info[0], allele_info[1])
            return new_allele
    return None

def create_chemicals(old_phenotype_feature):
    from model_new_schema.misc import Chemical as NewChemical
    chemicals = []
    if old_phenotype_feature.experiment is not None:
        chemical_infos = old_phenotype_feature.experiment.chemicals
        chemicals = [NewChemical(x[0]) for x in chemical_infos]
        return chemicals
    return None

def create_phenoevidence(old_phenotype_feature, key_to_reflink, key_to_phenotype):
    from model_new_schema.phenotype import Phenoevidence as NewPhenoevidence
    evidence_id = create_phenoevidence_id(old_phenotype_feature.id)
    reference_id = key_to_reflink[('PHENO_ANNOTATION_NO', old_phenotype_feature.id)].reference_id
    bioent_id = old_phenotype_feature.feature_id
    biocon_id = key_to_phenotype[create_phenotype_key(old_phenotype_feature.observable)].id

    new_phenoevidence = NewPhenoevidence(evidence_id, old_phenotype_feature.experiment_type, reference_id, None, old_phenotype_feature.source,
                                         old_phenotype_feature.mutant_type, old_phenotype_feature.qualifier, bioent_id, biocon_id,
                                         old_phenotype_feature.date_created, old_phenotype_feature.created_by)
    if old_phenotype_feature.experiment is not None:
        experiment = old_phenotype_feature.experiment
        new_phenoevidence.reporter = None if experiment.reporter == None else experiment.reporter[0]
        new_phenoevidence.reporter_desc = None if experiment.reporter == None else experiment.reporter[1]
        new_phenoevidence.strain_id = None if experiment.strain == None else experiment.strain[0]
        new_phenoevidence.strain_details = None if experiment.strain == None else experiment.strain[1]
        #new_phenoevidence.budding_index = None if experiment.budding_index == None else float(experiment.budding_index)
        #new_phenoevidence.glutathione_excretion = None if experiment.glutathione_excretion == None else float(experiment.glutathione_excretion)
        #new_phenoevidence.z_score = experiment.z_score
        #new_phenoevidence.relative_fitness_score = None if experiment.relative_fitness_score == None else float(experiment.relative_fitness_score)
        #new_phenoevidence.chitin_level = None if experiment.chitin_level == None else float(experiment.chitin_level)
    
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


def create_phenoevidence_chemical(chemical_info, evidence_id, key_to_chemical):
    from model_new_schema.phenotype import PhenoevidenceChemical as NewPhenoevidenceChemical
    chemical_id = key_to_chemical[chemical_info[0]].id
    chemical_amount = chemical_info[1]
    new_pheno_chemical = NewPhenoevidenceChemical(evidence_id, chemical_id, chemical_amount)
    return new_pheno_chemical

     
"""
---------------------Convert------------------------------
"""  

def convert_phenotype(old_session, new_session):

    from model_old_schema.phenotype import PhenotypeFeature as OldPhenotypeFeature, Phenotype as OldPhenotype
    from model_old_schema.reference import Reflink as OldReflink
    from model_old_schema.cv import CVTerm as OldCVTerm
    
    from model_new_schema.phenotype import Phenotype as NewPhenotype, Phenoevidence as NewPhenoevidence, PhenoevidenceChemical as NewPhenoevidenceChemical
    from model_new_schema.bioconcept import BioconAncestor as NewBioconAncestor, BioconRelation as NewBioconRelation
    from model_new_schema.misc import Allele as NewAllele, Chemical as NewChemical
    
    '''
    Convert Phenotypes
    '''
    print 'Phenotypes'
    start_time = datetime.datetime.now()
    
    #Cache phenotypes
    key_to_phenotype = cache(NewPhenotype, new_session)

    #Create new phenotypes if they don't exist, or update the database if they do.
    old_phenotypes = old_session.query(OldPhenotype).all()
    new_phenotypes = filter(None, [create_phenotype(x) for x in old_phenotypes])
    values_to_check = ['observable', 'phenotype_type']
    create_or_update_and_remove(new_phenotypes, key_to_phenotype, values_to_check, new_session)
    
    #Add definitions to phenotypes
    cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==6).all()
    for cv_term in cv_terms:
        phenotype_key = create_phenotype_key(cv_term.name)
        if phenotype_key in key_to_phenotype:
            new_phenotype = key_to_phenotype[phenotype_key]
            if new_phenotype.description != cv_term.definition:
                new_phenotype.description = cv_term.definition
                new_session.add(new_phenotype)
                
    ask_to_commit(new_session, start_time)

    
    '''
    Convert Alleles
    '''
    print 'Alleles'
    start_time = datetime.datetime.now()
    
    old_phenoevidences = old_session.query(OldPhenotypeFeature).all()

    #Cache alleles
    key_to_allele = cache(NewAllele, new_session)
    
    #Create new alleles if they don't exist, or update the database if they do.
    values_to_check = ['more_info']
    new_alleles = filter(None, [create_allele(x) for x in old_phenoevidences])
    create_or_update_and_remove(new_alleles, key_to_allele, values_to_check, new_session)
    
    ask_to_commit(new_session, start_time)

    
    '''
    Convert Chemicals
    '''
    print 'Chemicals'
    start_time = datetime.datetime.now()

    #Cache chemicals
    key_to_chemical = cache(NewChemical, new_session)
    
    #Create new chemicals if they don't exist, or update the database if they do.
    values_to_check = ['name']
    chemicals = []
    for old_phenoevidence in old_phenoevidences:
        chems = create_chemicals(old_phenoevidence)
        if chems != None:
            chemicals.extend(chems)
    create_or_update_and_remove(chemicals, key_to_chemical, values_to_check, new_session)
    
    ask_to_commit(new_session, start_time)
    
    '''
    Convert Phenoevidences
    '''
    print 'Phenoevidences'
    start_time = datetime.datetime.now()
    
    #Cache reflinks
    key_to_reflink = cache(OldReflink, old_session)
    
    #Cache phenoevidences
    key_to_phenoevidence = cache(NewPhenoevidence, new_session)

    #Create new phenoevidences if they don't exist, or update the database if they do.    
    new_phenoevidences = []
    for old_phenoevidence in old_phenoevidences:
        new_phenoevidence = create_phenoevidence(old_phenoevidence, key_to_reflink, key_to_phenotype)
        if new_phenoevidence is not None:
            new_phenoevidences.append(new_phenoevidence)
            
    values_to_check = ['experiment_type', 'reference_id', 'evidence_type', 'strain_id', 'source',
                       'bioent_id', 'biocon_id', 'date_created', 'created_by',
                       'mutant_type', 'qualifier', 'reporter', 'reporter_desc', 'strain_details', 
                       'conditions', 'details', 'experiment_details']
    create_or_update_and_remove(new_phenoevidences, key_to_phenoevidence, values_to_check, new_session)
            
    #Add alleles to phenoevidences
    for old_phenoevidence in old_phenoevidences:
        new_phenoevidence = key_to_phenoevidence[create_phenoevidence_id(old_phenoevidence.id)]
        if old_phenoevidence.experiment is not None:
            allele_info = old_phenoevidence.experiment.allele
            if allele_info is not None:
                allele_name = allele_info[0]
                allele_id = key_to_allele[allele_name].id
                if new_phenoevidence.mutant_allele_id != allele_id:
                    new_phenoevidence.mutant_allele_id = allele_id
                    new_session.add(new_phenoevidence)
                
    #Cache evidence_chemical
    key_to_phenoevidence_chemical = cache(NewPhenoevidenceChemical, new_session)
    
    values_to_check = ['evidence_id', 'chemical_id', 'chemical_amt']
    phenoevidence_chemicals = []
    #Create new evidence_chemical if they don't exist, or update the database if they do.
    for old_phenoevidence in old_phenoevidences:
        new_phenoevidence_id = create_phenoevidence_id(old_phenoevidence.id)
        if old_phenoevidence.experiment is not None:
            chemical_infos = old_phenoevidence.experiment.chemicals
            if chemical_infos is not None:   
                phenoevidence_chemicals.extend([create_phenoevidence_chemical(x, new_phenoevidence_id, key_to_chemical) for x in chemical_infos])
    create_or_update_and_remove(phenoevidence_chemicals, key_to_phenoevidence_chemical, values_to_check, new_session)

    ask_to_commit(new_session, start_time)
       


#     
#    #Add phenotype ontology
#    #Cache BioconRelations
#    bioconrel_oc = OutputCreator('bioconrel')
#    cache(NewBioconRelation, tuple_to_bioconrel, lambda x: (x.child_id, x.parent_id, x.bioconrel_type, x.relationship_type) if x.relationship_type == 'PHENOTYPE_ONTOLOGY' else None, new_session, bioconrel_oc)
#    
#    #Cache BioconAncestors
#    bioconanc_oc = OutputCreator('bioconanc')
#    cache(NewBioconAncestor, tuple_to_bioconanc, lambda x: (x.child_id, x.ancestor_id), new_session, bioconanc_oc)
#    
#    #Add bioconrels and bioconancs
#    for cv_term in cv_terms:
#        if cv_term.name in observable_to_phenotype:
#            child_id = observable_to_phenotype[cv_term.name].id
#            for parent in cv_term.parents:
#                if parent.name in observable_to_phenotype:
#                    parent_id = observable_to_phenotype[parent.name].id
#                    biocon_biocon = NewBioconRelation(None, parent_id, child_id, 'PHENOTYPE_ONTOLOGY', 'is a')
#                    add_or_check(biocon_biocon, tuple_to_bioconrel, (biocon_biocon.child_id, biocon_biocon.parent_id, biocon_biocon.bioconrel_type, biocon_biocon.relationship_type), [], new_session, bioconrel_oc)
#    bioconrel_oc.finished()
        
    #for cv_term in cv_terms:
    #    parents = list(cv_term.parents)
    #    while len(parents) > 0:
    #        parent = parents.pop()
    #        biocon_ancestor = NewBioconAncestor(observable_to_phenotype[parent.name].id, child_id)
    #        add_or_check(biocon_ancestor, tuple_to_bioconanc, (biocon_ancestor.child_id, biocon_ancestor.ancestor_id), [], new_session, bioconanc_oc)
            #parents.extend(parent.parents)
        
        
            
    
