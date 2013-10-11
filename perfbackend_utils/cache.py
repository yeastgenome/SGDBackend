'''
Created on Aug 9, 2013

@author: kpaskov
'''
from sqlalchemy.sql.expression import select

id_to_bioent = {}
id_to_reference = {}
bioent_key_to_id = {}

def cache_core(engine, meta):
    #Cache bioents
    #print 'Cache bioents'

    bioentities = meta.tables['bioentity']
    for bioent in engine.execute(select([bioentities])).fetchall():
        id_to_bioent[str(bioent.bioentity_id)] = bioent.json
        id_to_bioent[(bioent.format_name, getattr(bioent, 'class'))] = bioent.json
        id_to_bioent[(bioent.display_name, getattr(bioent, 'class'))] = bioent.json
        id_to_bioent[(bioent.dbxref, getattr(bioent, 'class'))] = bioent.json
        bioent_key_to_id[str(bioent.bioentity_id)] = bioent.bioentity_id
        bioent_key_to_id[(bioent.format_name, getattr(bioent, 'class'))] = bioent.bioentity_id
        bioent_key_to_id[(bioent.display_name, getattr(bioent, 'class'))] = bioent.bioentity_id
        bioent_key_to_id[(bioent.dbxref, getattr(bioent, 'class'))] = bioent.bioentity_id
                
    #print 'Cache references'
    #Cache references
    #from model_perf_schema.reference import Reference
    #for reference in query_all(Reference):
    #    id_to_reference[reference.id] = reference.json
        
def get_cached_bioent(bioent_repr, bioent_type=None):
    return get_cached_obj(id_to_bioent, bioent_repr, (bioent_repr, None if bioent_type is None else bioent_type.upper()))

def get_cached_obj(mapping, id_key, key):
    if id_key in mapping:
        return mapping[id_key]
    
    if key is not None and key in mapping:
        return mapping[key]
    
    return None

def get_bioent_id(identifier, bioent_type):
    key = (identifier, bioent_type)
    if identifier in bioent_key_to_id:
        return bioent_key_to_id[identifier]
    elif key in bioent_key_to_id:
        return bioent_key_to_id[key]
    return None

