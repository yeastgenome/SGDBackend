'''
Created on May 6, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import cache, create_or_update_and_remove, ask_to_commit, \
    prepare_schema_connection
import datetime
import model_new_schema
import model_old_schema

'''
 This code is used to convert phenotype data from the old schema to the new. It does this by
 creating new schema objects from the old, then comparing these new objects to those already
 stored in the new database. If a newly created object matches one that is already stored, the two
 are compared and the database fields are updated. If a newly created object does not match one that is 
 already stored, it is added to the database.
'''
"""
------------ Create --------------
"""
def create_phenotype_id(old_phenotype_id):
    return old_phenotype_id

def create_phenoevidence_id(old_evidence_id):
    return old_evidence_id

def create_phenotype_key(observable):
    name = observable.replace(' ', '_')
    name = name.replace('/', '-')
    return (name, 'PHENOTYPE')

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
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    new_phenotype = NewPhenotype(create_phenotype_id(old_phenotype.id), old_phenotype.observable, create_phenotype_type(old_phenotype.observable), None,
                                 old_phenotype.date_created, old_phenotype.created_by)
    return new_phenotype

def create_allele(old_phenotype_feature):
    from model_new_schema.misc import Allele as NewAllele
    if old_phenotype_feature.experiment is not None:
        allele_info = old_phenotype_feature.experiment.allele
        if allele_info is not None:
            new_allele = NewAllele(allele_info[0], None)
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

def convert(old_session_maker, new_session_maker):

    from model_old_schema.phenotype import PhenotypeFeature as OldPhenotypeFeature, Phenotype as OldPhenotype
    from model_old_schema.reference import Reflink as OldReflink
    from model_old_schema.cv import CVTerm as OldCVTerm
    
    # Convert phenotypes
    print 'Phenotypes'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        old_phenotypes = old_session.query(OldPhenotype).all()
        cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==6).all()

        convert_phenotypes(new_session, old_phenotypes, cv_terms)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
    
    # Convert alleles
    print 'Alleles'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        old_phenoevidences = old_session.query(OldPhenotypeFeature).all()

        convert_alleles(new_session, old_phenoevidences)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
    
    # Convert chemicals
    print 'Chemicals'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        convert_chemicals(new_session, old_phenoevidences)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
        
    # Convert phenoevidences
    print 'Phenoevidences'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        old_reflinks = old_session.query(OldReflink).all()
        
        convert_phenoevidences(new_session, old_phenoevidences, old_reflinks)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
        
    # Convert phenoevidence_chemicals
    print 'Phenoevidence_Chemicals'            
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
                
        convert_phenoevidence_chemicals(new_session, old_phenoevidences)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
        
    # Update gene counts
    print 'Phenotype gene counts'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
                
        update_gene_counts(new_session)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close() 
        
    # Convert biocon_relations
    print 'Biocon_relations'            
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        old_cv_terms = old_session.query(OldCVTerm).all()
                
        convert_biocon_relations(new_session, old_cv_terms)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
        
    # Convert biocon_ancestors
    print 'Biocon_ancestors'            
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
                        
        convert_biocon_ancestors(new_session, old_cv_terms)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
        
def convert_phenotypes(new_session, old_phenotypes, cv_terms):
    '''
    Convert Phenotypes
    '''
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    
    #Cache phenotypes
    key_to_phenotype = cache(NewPhenotype, new_session)

    #Create new phenotypes if they don't exist, or update the database if they do.
    new_phenotypes = filter(None, [create_phenotype(x) for x in old_phenotypes])
    values_to_check = ['observable', 'phenotype_type', 'biocon_type', 'official_name']
    
    #Add definitions to phenotypes
    for cv_term in cv_terms:
        phenotype_key = create_phenotype_key(cv_term.name)
        if phenotype_key in key_to_phenotype:
            new_phenotype = key_to_phenotype[phenotype_key]
            if new_phenotype.description != cv_term.definition:
                new_phenotype.description = cv_term.definition
    create_or_update_and_remove(new_phenotypes, key_to_phenotype, values_to_check, new_session)

                
def convert_alleles(new_session, old_phenoevidences):
    '''
    Convert Alleles
    '''
    from model_new_schema.misc import Allele as NewAllele

    #Cache alleles
    key_to_allele = cache(NewAllele, new_session)
    
    #Create new alleles if they don't exist, or update the database if they do.
    values_to_check = ['more_info']
    new_alleles = filter(None, [create_allele(x) for x in old_phenoevidences])
    create_or_update_and_remove(new_alleles, key_to_allele, values_to_check, new_session)
    
def convert_chemicals(new_session, old_phenoevidences):
    '''
    Convert Chemicals
    '''
    from model_new_schema.misc import Chemical as NewChemical

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
    
def convert_phenoevidences(new_session, old_phenoevidences, old_reflinks):
    '''
    Convert Phenoevidences
    '''
    from model_new_schema.phenotype import Phenoevidence as NewPhenoevidence, Phenotype as NewPhenotype
    from model_new_schema.misc import Allele as NewAllele
    
    #Cache reflinks
    key_to_reflink = dict([((x.col_name, x.primary_key), x) for x in old_reflinks])
    
    #Cache phenotypes, alleles, and phenoevidences
    key_to_phenotype = cache(NewPhenotype, new_session)
    key_to_allele = cache(NewAllele, new_session)
    key_to_phenoevidence = cache(NewPhenoevidence, new_session)

    #Create new phenoevidences if they don't exist, or update the database if they do.    
    new_phenoevidences = []
    for old_phenoevidence in old_phenoevidences:
        new_phenoevidence = create_phenoevidence(old_phenoevidence, key_to_reflink, key_to_phenotype)
        if new_phenoevidence is not None:
            #Add alleles to phenoevidence
            if old_phenoevidence.experiment is not None:
                allele_info = old_phenoevidence.experiment.allele
                if allele_info is not None:
                    allele_name = allele_info[0]
                    new_phenoevidence.mutant_allele_id = key_to_allele[allele_name].id
                    new_phenoevidence.allele_info = allele_info[1]
            new_phenoevidences.append(new_phenoevidence)
                    
    values_to_check = ['experiment_type', 'reference_id', 'evidence_type', 'strain_id', 'source',
                       'bioent_id', 'biocon_id', 'date_created', 'created_by',
                       'mutant_type', 'qualifier', 'reporter', 'reporter_desc', 'strain_details', 
                       'conditions', 'details', 'experiment_details', 'allele_info', 'mutant_allele_id']
    create_or_update_and_remove(new_phenoevidences, key_to_phenoevidence, values_to_check, new_session)
    
def convert_phenoevidence_chemicals(new_session, old_phenoevidences):
    '''
    Convert Phenoevidence_chemicals
    '''
    from model_new_schema.phenotype import PhenoevidenceChemical as NewPhenoevidenceChemical
    from model_new_schema.misc import Chemical as NewChemical
    
    #Cache evidence_chemical and chemical
    key_to_phenoevidence_chemical = cache(NewPhenoevidenceChemical, new_session)
    key_to_chemical = cache(NewChemical, new_session)
    
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

def update_gene_counts(new_session):
    '''
    Update goterm gene counts
    '''
    from model_new_schema.phenotype import Phenoevidence as NewPhenoevidence, Phenotype as NewPhenotype

    phenotypes = new_session.query(NewPhenotype).all()
    phenoevidences = new_session.query(NewPhenoevidence).all()
    biocon_id_to_bioent_ids = {}
    
    for phenotype in phenotypes:
        biocon_id_to_bioent_ids[phenotype.id] = set()
        
    for phenoevidence in phenoevidences:
        biocon_id_to_bioent_ids[phenoevidence.biocon_id].add(phenoevidence.bioent_id)
        
    num_changed = 0
    for phenotype in phenotypes:
        count = len(biocon_id_to_bioent_ids[phenotype.id])
        if count != phenotype.direct_gene_count:
            phenotype.direct_gene_count = count
            num_changed = num_changed + 1
    print 'In total ' + str(num_changed) + ' changed.'

def convert_biocon_relations(new_session, old_cv_terms):
    '''
    Convert biocon_relations (add phenotype ontology)
    '''         
    from model_new_schema.bioconcept import BioconRelation as NewBioconRelation
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    
    #Cache BioconRelations and phenotypes
    key_to_biocon_relations = cache(NewBioconRelation, new_session, bioconrel_type='PHENOTYPE_ONTOLOGY')
    key_to_phenotype = cache(NewPhenotype, new_session)
    
    #Create new biocon_relations if they don't exist, or update the database if they do.
    bioconrels = []
    for cv_term in old_cv_terms:
        child_phenotype_key = create_phenotype_key(cv_term.name)
        if child_phenotype_key in key_to_phenotype:
            child_id = key_to_phenotype[child_phenotype_key].id
            for parent in cv_term.parents:
                parent_phenotype_key = create_phenotype_key(parent.name)
                if parent_phenotype_key in key_to_phenotype:
                    parent_id = key_to_phenotype[parent_phenotype_key].id
                    biocon_biocon = NewBioconRelation(parent_id, child_id, 'PHENOTYPE_ONTOLOGY', 'is a')
                    bioconrels.append(biocon_biocon)
    create_or_update_and_remove(bioconrels, key_to_biocon_relations, [], new_session)
    
def convert_biocon_ancestors(new_session, old_cv_terms):
    '''
    Convert biocon_ancestors (continue adding phenotype ontology)
    '''
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    from model_new_schema.bioconcept import BioconAncestor as NewBioconAncestor
    
    #Cache BioconAncestors and phenotypes
    key_to_biocon_ancestors = cache(NewBioconAncestor, new_session, bioconanc_type='PHENOTYPE_ONTOLOGY')
    key_to_phenotype = cache(NewPhenotype, new_session)

    biocon_ancestors = []
    for cv_term in old_cv_terms:
        child_phenotype_key = create_phenotype_key(cv_term.name)
        if child_phenotype_key in key_to_phenotype:
            child_id = key_to_phenotype[child_phenotype_key].id
            family_id_to_generation = {}
            current_gen = list(cv_term.parents)
            next_gen = []
            generation = 1
            while len(current_gen) > 0:
                for parent in current_gen:
                    parent_phenotype_key = create_phenotype_key(parent.name)
                    if parent_phenotype_key in key_to_phenotype:
                        parent_id = key_to_phenotype[parent_phenotype_key].id
                        if parent_id not in family_id_to_generation:
                            family_id_to_generation[parent_id] = generation
                            next_gen.extend(parent.parents)
                del current_gen[:]
                current_gen.extend(next_gen)
                del next_gen[:]
                generation = generation + 1
            biocon_ancestors.extend([NewBioconAncestor(x, child_id, 'PHENOTYPE_ONTOLOGY', y) for x, y in family_id_to_generation.iteritems()])
    create_or_update_and_remove(biocon_ancestors, key_to_biocon_ancestors, ['generation'], new_session)   


if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)
    
    
