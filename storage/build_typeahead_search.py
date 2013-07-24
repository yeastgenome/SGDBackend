'''
Created on Apr 19, 2013

@author: kpaskov
'''

'''
Created on May 31, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, \
    prepare_schema_connection, cache_by_key, execute_conversion
import model_new_schema
import model_old_schema
from schema_conversion.output_manager import write_to_output_file


def create_typeahead(obj, f):
    from model_new_schema.search import Typeahead as NewTypeahead
    
    return NewTypeahead(f(obj).lower(), obj.type, obj.id)

"""
---------------------Convert------------------------------
"""   

def build(old_session_maker, new_session_maker, ask=True):

    # Convert Locus
    write_to_output_file('Locus')
    execute_conversion(build_locus, old_session_maker, new_session_maker, ask) 
    
    # Convert Go
    write_to_output_file('Go')
    execute_conversion(build_go, old_session_maker, new_session_maker, ask) 
    
    # Convert Reference
    #write_to_output_file('Reference')
    #execute_conversion(build_reference, old_session_maker, new_session_maker, ask) 

    
f_display_name = lambda x: x.display_name;
f_format_name = lambda x: x.format_name;

def build_locus(new_session):
    
    from model_new_schema.bioentity import Locus
    from model_new_schema.search import Typeahead
    
    #Cache bioentities
    key_to_bioentity = cache_by_key(Locus, new_session)
    key_to_typeahead = cache_by_key(Typeahead, new_session, bio_type = "LOCUS")
    
    #Create new genes if they don't exist, or update the database if they do. 
    new_typeaheads = set([create_typeahead(x, f_display_name) for x in key_to_bioentity.values()])
    new_typeaheads.update([create_typeahead(x, f_format_name) for x in key_to_bioentity.values()])
    
    success = create_or_update_and_remove(new_typeaheads, key_to_typeahead, [], new_session)
    return success
        
def build_go(new_session):
    
    from model_new_schema.go import Go
    from model_new_schema.search import Typeahead
    
    #Cache go terms
    key_to_go = cache_by_key(Go, new_session)
    key_to_typeahead = cache_by_key(Typeahead, new_session, bio_type = "GO")
    
    #Create new genes if they don't exist, or update the database if they do. 
    new_typeaheads = set([create_typeahead(x, f_display_name) for x in key_to_go.values()])
    
    success = create_or_update_and_remove(new_typeaheads, key_to_typeahead, [], new_session)
    return success

def build_reference(new_session):
    
    from model_new_schema.reference import Reference
    from model_new_schema.search import Typeahead
    
    #Cache references
    key_to_ref = cache_by_key(Reference, new_session)
    key_to_typeahead = cache_by_key(Typeahead, new_session, bio_type = "REFERENCE")
    
    #Create new genes if they don't exist, or update the database if they do. 
    new_typeaheads = set([create_typeahead(x, lambda x: x.citation) for x in key_to_ref.values()])
    new_typeaheads.update([create_typeahead(x, lambda x: str(x.pubmed_id)) for x in key_to_ref.values()])
    
    success = create_or_update_and_remove(new_typeaheads, key_to_typeahead, [], new_session)
    return success


if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    build(old_session_maker, new_session_maker, False)   
   

