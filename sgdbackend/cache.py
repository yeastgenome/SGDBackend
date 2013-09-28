'''
Created on Aug 9, 2013

@author: kpaskov
'''
from sgdbackend.obj_to_json import bioent_to_json, experiment_to_json, \
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
        id_to_bioent[bioent.unique_key()] = json_form
        id_to_bioent[(bioent.display_name, bioent.class_type)] = json_form
       
    #print 'Cache biocons' 
    #Cache biocons
    for biocon in get_all_biocons():
        json_form = biocon_to_json(biocon)
        id_to_biocon[biocon.id] = json_form
        id_to_biocon[biocon.unique_key()] = json_form
        
        if biocon.class_type == 'GO':
            id_to_biocon[(biocon.go_go_id, 'GO')] = json_form
        
    #print 'Cache experiments'
    #Cache experiments
    for experiment in get_all_experiments():
        json_form = experiment_to_json(experiment)
        id_to_experiment[experiment.id] = json_form
        id_to_experiment[experiment.unique_key()] = json_form
        
    #print 'Cache strains'
    #Cache strains
    for strain in get_all_strains():
        json_form = strain_to_json(strain)
        id_to_strain[strain.id] = json_form
        id_to_strain[strain.unique_key()] = json_form
        
    #print 'Cache references'
    #Cache references
    for reference in get_all_references():
        json_form = reference_to_json(reference)
        id_to_reference[reference.id] = json_form
        id_to_reference[reference.format_name] = json_form
        
def get_cached_bioent(bioent_repr, bioent_type=None):
    return get_cached_obj(id_to_bioent, bioent_repr, (bioent_repr, None if bioent_type is None else bioent_type.upper()))

def get_cached_biocon(biocon_repr, biocon_type=None):
    return get_cached_obj(id_to_biocon, biocon_repr, (biocon_repr, None if biocon_type is None else biocon_type.upper()))

def get_cached_experiment(experiment_repr):
    return get_cached_obj(id_to_experiment, experiment_repr, experiment_repr)

def get_cached_strain(strain_repr):
    return get_cached_obj(id_to_strain, strain_repr, strain_repr)

def get_cached_reference(reference_repr):
    return get_cached_obj(id_to_reference, reference_repr, reference_repr)


def get_cached_obj(mapping, id_key, key):
    int_id_key = None
    if id_key is not None:
        try:
            int_id_key = int(id_key)
        except ValueError:
            pass
    
    if int_id_key is not None and int_id_key in mapping:
        return mapping[int_id_key]
    
    if key is not None and key in mapping:
        return mapping[key]
    
    return None

