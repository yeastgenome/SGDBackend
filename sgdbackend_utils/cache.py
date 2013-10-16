'''
Created on Aug 9, 2013

@author: kpaskov
'''
from obj_to_json import bioent_to_json, experiment_to_json, \
    strain_to_json, biocon_to_json, reference_to_json, locus_to_json
from sgdbackend_query.query_biocon import get_all_biocons
from sgdbackend_query.query_bioent import get_all_bioents
from sgdbackend_query.query_evidence import get_all_experiments, get_all_strains
from sgdbackend_query.query_reference import get_all_references


id_to_bioent = {}
id_to_biocon = {}
id_to_experiment = {}
id_to_strain = {}
id_to_reference = {}

def cache_core():
    #print 'Cache bioents'
    #Cache bioents
    for bioent in get_all_bioents():
        if bioent.class_type == 'LOCUS':
            json_form = locus_to_json(bioent)
        else:
            json_form = bioent_to_json(bioent)
        id_to_bioent[bioent.id] = json_form
       
    #print 'Cache biocons' 
    #Cache biocons
    for biocon in get_all_biocons():
        json_form = biocon_to_json(biocon)
        id_to_biocon[biocon.id] = json_form
        
    #print 'Cache experiments'
    #Cache experiments
    for experiment in get_all_experiments():
        json_form = experiment_to_json(experiment)
        id_to_experiment[experiment.id] = json_form
        
    #print 'Cache strains'
    #Cache strains
    for strain in get_all_strains():
        json_form = strain_to_json(strain)
        id_to_strain[strain.id] = json_form
        
    #print 'Cache references'
    #Cache references
    for reference in get_all_references():
        json_form = reference_to_json(reference)
        id_to_reference[reference.id] = json_form

