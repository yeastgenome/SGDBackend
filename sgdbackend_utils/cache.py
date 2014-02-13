'''
Created on Aug 9, 2013

@author: kpaskov
'''
from obj_to_json import bioent_to_json, experiment_to_json, strain_to_json, \
    biocon_to_json, reference_to_json, locus_to_json, complex_to_json
from sgdbackend_query import get_all
from sgdbackend_utils.obj_to_json import bioitem_to_json, source_to_json, \
    chemical_to_json, go_to_json, phenotype_to_json, protein_to_json


id_to_bioent = {}
id_to_biocon = {}
id_to_bioitem = {}
id_to_experiment = {}
id_to_strain = {}
id_to_reference = {}
id_to_source = {}
id_to_chem = {}

word_to_bioent_id = {}

def cache_core():

    print 'Cache bioents'
    #Cache bioents
    from model_new_schema.bioentity import Bioentity
    for bioent in get_all(Bioentity):
        json_form = bioent_to_json(bioent)
        id_to_bioent[bioent.id] = json_form
        
    from model_new_schema.bioentity import Locus
    for bioent in get_all(Locus, join="aliases"):
        json_form = locus_to_json(bioent)
        id_to_bioent[bioent.id] = json_form

    from model_new_schema.bioentity import Protein
    for bioent in get_all(Protein):
        json_form = protein_to_json(bioent, id_to_bioent)
        id_to_bioent[bioent.id] = json_form

    create_word_to_bioent_id()
       
    print 'Cache biocons' 
    #Cache biocons
    from model_new_schema.bioconcept import Bioconcept
    for biocon in get_all(Bioconcept):
        json_form = biocon_to_json(biocon)
        id_to_biocon[biocon.id] = json_form
        
    from model_new_schema.bioconcept import Go
    for biocon in get_all(Go, join="aliases"):
        json_form = go_to_json(biocon)
        id_to_biocon[biocon.id] = json_form
        
    from model_new_schema.bioconcept import Phenotype
    for biocon in get_all(Phenotype):
        json_form = phenotype_to_json(biocon)
        id_to_biocon[biocon.id] = json_form

    from model_new_schema.bioentity import Complex
    for bioent in get_all(Complex):
        json_form = complex_to_json(bioent, id_to_biocon)
        id_to_bioent[bioent.id] = json_form
        
    print 'Cache bioitems' 
    #Cache bioitems
    from model_new_schema.bioitem import Bioitem
    for bioitem in get_all(Bioitem):
        json_form = bioitem_to_json(bioitem)
        id_to_bioitem[bioitem.id] = json_form
        
    print 'Cache experiments'
    #Cache experiments
    from model_new_schema.evelements import Experiment
    for experiment in get_all(Experiment):
        json_form = experiment_to_json(experiment)
        id_to_experiment[experiment.id] = json_form
        
    print 'Cache strains'
    #Cache strains
    from model_new_schema.evelements import Strain
    for strain in get_all(Strain):
        json_form = strain_to_json(strain)
        id_to_strain[strain.id] = json_form
        
    print 'Cache references'
    #Cache references
    from model_new_schema.reference import Reference
    for reference in get_all(Reference, "journal"):
        json_form = reference_to_json(reference)
        id_to_reference[reference.id] = json_form
        
    print 'Cache sources'
    #Cache sources
    from model_new_schema.evelements import Source
    for source in get_all(Source):
        json_form = source_to_json(source)
        id_to_source[source.id] = json_form

    print 'Cache chemicals'
    #Cache sources
    from model_new_schema.chemical import Chemical
    for chem in get_all(Chemical):
        json_form = chemical_to_json(chem)
        id_to_chem[chem.id] = json_form

def create_word_to_bioent_id():
    for bioent_id, bioent in id_to_bioent.iteritems():
        if bioent['class_type'] == 'LOCUS':
            word_to_bioent_id[bioent['display_name'].upper()] = bioent_id
            word_to_bioent_id[bioent['format_name'].upper()] = bioent_id
    return word_to_bioent_id

