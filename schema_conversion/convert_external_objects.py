'''
Created on May 23, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import cache, create_or_update_and_remove, ask_to_commit, \
    prepare_schema_connection
import datetime
import model_new_schema
import model_old_schema


"""
---------------------Create------------------------------
"""

def create_externalobj(dbxref):
    from model_new_schema.misc import ExternalObject as NewExternalObject#, Url as NewUrl
    externalobj = None
    
    bioent_id = None
    feature_ids = set(dbxref.feature_ids)
    if len(feature_ids) == 1:
        bioent_id = dbxref.feature_ids[0]
    elif len(feature_ids) > 1:
        print 'More than one feature associated with this dbxref.'
            
    if dbxref.source == 'AspGD':
        url = 'http://www.aspgd.org/cgi-bin/locus.pl?locus=' + dbxref.dbxref_id
        externalobj = NewExternalObject(dbxref.id, dbxref.dbxref_id, dbxref.source, 
                                     dbxref.dbxref_id, bioent_id, None)
        if not check_url(url):
            print 'Broken url'
        #externalobj.url = NewUrl(dbxref.id, url, dbxref.source)
        
    return externalobj

"""
---------------------Convert------------------------------
"""  

def convert(old_session_maker, new_session_maker):

    from model_old_schema.dbxref import Dbxref as OldDbxref
    
    # Convert external objects
    print 'External objects'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        old_dbxrefs = old_session.query(OldDbxref).all()

        convert_externalobjs(new_session, old_dbxrefs)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
        
def convert_externalobjs(new_session, old_externalobjs):
    '''
    Convert External objects
    '''
    from model_new_schema.misc import ExternalObject as NewExternalObject
    
    #Cache external objects
    key_to_externalobj = cache(NewExternalObject, new_session, source='AspGD')

    #Create new external objects if they don't exist, or update the database if they do.
    new_externalobjs = filter(None, [create_externalobj(x) for x in old_externalobjs])
    values_to_check = ['id', 'external_id', 'primary_url_id', 'assoc_bioent_id', 'assoc_biocon_id']
    create_or_update_and_remove(new_externalobjs, key_to_externalobj, values_to_check, new_session)

        
        
    
if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)