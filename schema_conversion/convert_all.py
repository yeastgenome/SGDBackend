'''
Created on Jul 3, 2013

@author: kpaskov
'''

from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import prepare_schema_connection, convert_reference, \
    convert_bioentity, convert_evelements
import model_new_schema
import model_old_schema
import sys

if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    
    print '----------------------------------------'
    print 'Convert Bioentities'
    print '----------------------------------------'
    try:
        convert_bioentity.convert(old_session_maker, new_session_maker, ask=False)  
    except Exception:
        print "Unexpected error:", sys.exc_info()[0]
        
    print '----------------------------------------'
    print 'Convert References'
    print '----------------------------------------'
    try:
        convert_reference.convert(old_session_maker, new_session_maker, ask=False)
    except Exception:
        print "Unexpected error:", sys.exc_info()[0]
      
    print '----------------------------------------'
    print 'Convert Evelements'
    print '----------------------------------------'  
    try:
        convert_evelements.convert(old_session_maker, new_session_maker, ask=False)
    except Exception:
        print "Unexpected error:", sys.exc_info()[0]