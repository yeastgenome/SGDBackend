'''
Created on May 6, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, ask_to_commit, \
    prepare_schema_connection, cache_by_key, cache_by_id, create_format_name, \
    create_or_update
from schema_conversion.auxillary_tables import update_biocon_gene_counts, \
    convert_biocon_ancestors
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
    display_name = old_phenotype.observable
    format_name = create_format_name(display_name)
    new_phenotype = NewPhenotype(create_phenotype_id(old_phenotype.id), display_name, format_name,
                                 None, create_phenotype_type(old_phenotype.observable),
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

def create_phenoevidence(old_phenotype_feature, key_to_reflink, key_to_phenotype, id_to_reference, id_to_bioent):
    from model_new_schema.phenotype import Phenoevidence as NewPhenoevidence
    evidence_id = create_phenoevidence_id(old_phenotype_feature.id)
    reference_id = key_to_reflink[('PHENO_ANNOTATION_NO', old_phenotype_feature.id)].reference_id
    if reference_id not in id_to_reference:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    bioent_id = old_phenotype_feature.feature_id
    if bioent_id not in id_to_bioent:
        print 'Bioentity does not exist. ' + str(bioent_id)
        return None
    
    phenotype_key = create_phenotype_key(old_phenotype_feature.observable)
    if phenotype_key not in key_to_phenotype:
        print 'Phenotype does not exist. ' + str(phenotype_key)
        return None
    biocon_id = key_to_phenotype[phenotype_key].id

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

def create_chemicals(expt_property):
    from model_new_schema.chemical import Chemical as NewChemical

    display_name = expt_property.value
    format_name = create_format_name(display_name)
    new_chemical = NewChemical(display_name, format_name, 'SGD', expt_property.date_created, expt_property.created_by)
    return new_chemical

def create_phenoevidence_chemical(chemical_info, evidence_id, key_to_chemical, id_to_phenoevidence):
    from model_new_schema.phenotype import PhenoevidenceChemical as NewPhenoevidenceChemical
    chemical_key = create_format_name(chemical_info[0])
    if chemical_key not in key_to_chemical:
        print 'Chemical does not exist. ' + chemical_key
        return None
    chemical_id = key_to_chemical[chemical_key].id
    chemical_amount = chemical_info[1]
    
    if evidence_id not in id_to_phenoevidence:
        print 'Phenoevidence does not exist. ' + str(evidence_id)
        return None
    
    new_pheno_chemical = NewPhenoevidenceChemical(evidence_id, chemical_id, chemical_amount)
    return new_pheno_chemical
  
"""
---------------------Convert------------------------------
"""  

def convert(old_session_maker, new_session_maker):

    from model_old_schema.phenotype import PhenotypeFeature as OldPhenotypeFeature, Phenotype as OldPhenotype, ExperimentProperty as OldExperimentProperty
    from model_old_schema.reference import Reflink as OldReflink
    from model_old_schema.cv import CVTerm as OldCVTerm
    
#    # Convert phenotypes
#    print 'Phenotypes'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_phenotypes = old_session.query(OldPhenotype).all()
#        old_cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==6).all()
#
#        success=False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_phenotypes(new_session, old_phenotypes, old_cv_terms)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
#    
    # Convert alleles
    print 'Alleles'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        old_phenoevidences = old_session.query(OldPhenotypeFeature).all()

        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_alleles(new_session, old_phenoevidences)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
#        
#    # Convert phenoevidences
#    print 'Phenoevidences'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_reflinks = old_session.query(OldReflink).all()
#
#        success=False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_phenoevidences(new_session, old_phenoevidences, old_reflinks)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
      
    # Convert chemicals
    print 'Chemicals'            
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        old_expt_properties = old_session.query(OldExperimentProperty).filter(OldExperimentProperty.type=='Chemical_pending').all()
        
        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_chemicals(new_session, old_expt_properties)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
          
    # Convert phenoevidence_chemicals
    print 'Phenoevidence_Chemicals'            
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        
        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_phenoevidence_chemicals(new_session, old_phenoevidences)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
#        
#    # Update gene counts
#    print 'Phenotype gene counts'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        
#        new_session = new_session_maker()        
#        from model_new_schema.phenotype import Phenotype as NewPhenotype, Phenoevidence as NewPhenoevidence
#        update_biocon_gene_counts(new_session, NewPhenotype, NewPhenoevidence)
#        ask_to_commit(new_session, start_time)  
#    finally:
#        old_session.close()
#        new_session.close() 
#        
#    # Convert biocon_relations
#    print 'Biocon_relations'            
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==6).all()
#        
#        success=False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_biocon_relations(new_session, old_cv_terms)
#            ask_to_commit(new_session, start_time) 
#            new_session.close() 
#    finally:
#        old_session.close()
#        new_session.close()
#        
#    # Convert biocon_ancestors
#    print 'Biocon_ancestors'            
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        
#        new_session = new_session_maker()                
#        success = convert_biocon_ancestors(new_session, 'PHENOTYPE_ONTOLOGY', 4)
#        ask_to_commit(new_session, start_time)  
#    finally:
#        old_session.close()
#        new_session.close()
        
def convert_phenotypes(new_session, old_phenotypes, cv_terms):
    '''
    Convert Phenotypes
    '''
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    
    #Cache phenotypes
    key_to_phenotype = cache_by_key(NewPhenotype, new_session)

    #Create new phenotypes if they don't exist, or update the database if they do.
    new_phenotypes = filter(None, [create_phenotype(x) for x in old_phenotypes])
    new_key_to_phenotypes = dict([(x.unique_key(), x) for x in new_phenotypes])
    values_to_check = ['phenotype_type', 'biocon_type', 'display_name', 'format_name', 'description']
    
    #Add definitions to phenotypes
    for cv_term in cv_terms:
        phenotype_key = create_phenotype_key(cv_term.name)
        if phenotype_key in new_key_to_phenotypes:
            new_phenotype = new_key_to_phenotypes[phenotype_key]
            new_phenotype.description = cv_term.definition
            
    success = create_or_update_and_remove(new_phenotypes, key_to_phenotype, values_to_check, new_session)
    return success
                
def convert_alleles(new_session, old_phenoevidences):
    '''
    Convert Alleles
    '''
    from model_new_schema.misc import Allele as NewAllele
    #May be necessary so that alleles can be removed.
    from model_new_schema.phenotype import Phenoevidence

    #Cache alleles
    key_to_allele = cache_by_key(NewAllele, new_session)
    
    #Create new alleles if they don't exist, or update the database if they do.
    values_to_check = ['more_info']
    new_alleles = filter(None, [create_allele(x) for x in old_phenoevidences])
    success = create_or_update_and_remove(new_alleles, key_to_allele, values_to_check, new_session)
    return success

def convert_chemicals(new_session, old_expt_properties):
    '''
    Convert Chemical
    '''
    from model_new_schema.chemical import Chemical as NewChemical
    #Cache chemicals
    key_to_chemical = cache_by_key(NewChemical, new_session)
    
    #Create new chemicals if they don't exist, or update the database if they do.
    values_to_check = []
    new_chemicals = [create_chemicals(x) for x in old_expt_properties]
    success = create_or_update(new_chemicals, key_to_chemical, values_to_check, new_session)
    return success
    
def convert_phenoevidences(new_session, old_phenoevidences, old_reflinks):
    '''
    Convert Phenoevidences
    '''
    from model_new_schema.phenotype import Phenoevidence as NewPhenoevidence, Phenotype as NewPhenotype
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.misc import Allele as NewAllele
    
    #Cache reflinks
    key_to_reflink = dict([((x.col_name, x.primary_key), x) for x in old_reflinks])
    
    #Cache phenotypes, alleles, and phenoevidences
    key_to_phenotype = cache_by_key(NewPhenotype, new_session)
    key_to_allele = cache_by_key(NewAllele, new_session)
    key_to_phenoevidence = cache_by_key(NewPhenoevidence, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    id_to_bioent = cache_by_id(NewBioentity, new_session)

    #Create new phenoevidences if they don't exist, or update the database if they do.    
    new_phenoevidences = []
    for old_phenoevidence in old_phenoevidences:
        new_phenoevidence = create_phenoevidence(old_phenoevidence, key_to_reflink, key_to_phenotype, id_to_reference, id_to_bioent)
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
    success = create_or_update_and_remove(new_phenoevidences, key_to_phenoevidence, values_to_check, new_session)
    return success
    
def convert_phenoevidence_chemicals(new_session, old_phenoevidences):
    '''
    Convert Phenoevidence_chemicals
    '''
    from model_new_schema.phenotype import PhenoevidenceChemical as NewPhenoevidenceChemical, Phenoevidence as NewPhenoevidence
    from model_new_schema.chemical import Chemical as NewChemical
    
    #Cache evidence_chemical and chemical
    key_to_phenoevidence_chemical = cache_by_key(NewPhenoevidenceChemical, new_session)
    key_to_chemical = cache_by_key(NewChemical, new_session)
    id_to_phenoevidence = cache_by_id(NewPhenoevidence, new_session)
    
    values_to_check = ['evidence_id', 'chemical_id', 'chemical_amt']
    phenoevidence_chemicals = []
    #Create new evidence_chemical if they don't exist, or update the database if they do.
    for old_phenoevidence in old_phenoevidences:
        new_phenoevidence_id = create_phenoevidence_id(old_phenoevidence.id)
        if old_phenoevidence.experiment is not None:
            chemical_infos = old_phenoevidence.experiment.chemicals
            if chemical_infos is not None:   
                phenoevidence_chemicals.extend([create_phenoevidence_chemical(x, new_phenoevidence_id, key_to_chemical, id_to_phenoevidence) for x in chemical_infos])
    success = create_or_update_and_remove(phenoevidence_chemicals, key_to_phenoevidence_chemical, values_to_check, new_session)
    return success

def convert_biocon_relations(new_session, old_cv_terms):
    '''
    Convert biocon_relations (add phenotype ontology)
    '''         
    from model_new_schema.bioconcept import BioconRelation as NewBioconRelation
    from model_new_schema.phenotype import Phenotype as NewPhenotype
    
    #Cache BioconRelations and phenotypes
    key_to_biocon_relations = cache_by_key(NewBioconRelation, new_session, bioconrel_type='PHENOTYPE_ONTOLOGY')
    key_to_phenotype = cache_by_key(NewPhenotype, new_session)
    
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
    success = create_or_update_and_remove(bioconrels, key_to_biocon_relations, [], new_session)
    return success

if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)
    
    
