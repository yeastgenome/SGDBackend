'''
Created on Jan 16, 2013

@author: kpaskov
'''
from model_new_schema.config import DBTYPE as NEW_DBTYPE, DBHOST as NEW_DBHOST, \
    DBNAME as NEW_DBNAME, SCHEMA as NEW_SCHEMA, DBUSER as NEW_DBUSER, \
    DBPASS as NEW_DBPASS
from model_new_schema.model import Model as NewModel
from model_old_schema.config import DBTYPE as OLD_DBTYPE, DBHOST as OLD_DBHOST, \
    DBNAME as OLD_DBNAME, SCHEMA as OLD_SCHEMA, DBUSER as OLD_DBUSER, \
    DBPASS as OLD_DBPASS
from model_old_schema.model import Model as OldModel
from schema_conversion.old_to_new import feature_to_bioent
import model_new_schema
import model_old_schema

def convert():
    old_model = OldModel(OLD_DBTYPE, OLD_DBHOST, OLD_DBNAME, OLD_SCHEMA)
    old_model.connect(OLD_DBUSER, OLD_DBPASS)
    
    new_model = NewModel(NEW_DBTYPE, NEW_DBHOST, NEW_DBNAME, NEW_SCHEMA)
    new_model.connect(NEW_DBUSER, NEW_DBPASS)
    
    convert_features_to_bioents(old_model, new_model)
    
def convert_features_to_bioents(old_model, new_model):
    print "Convert Features to Bioentities"
    from model_old_schema.feature import Feature as OldFeature
    fs = old_model.execute(model_old_schema.model.get(OldFeature), OLD_DBUSER)
    
    count = 0;
    for f in fs:
        b = feature_to_bioent(f)
    
        from model_new_schema.bioentity import Bioentity as NewBioentity
        b_already_in_new_db = new_model.execute(model_new_schema.model.get_first(NewBioentity, id=b.id), NEW_DBUSER)

        new_model.execute(model_new_schema.model.add(b), NEW_DBUSER)
        
        if b_already_in_new_db is None:
            new_model.execute(model_new_schema.model.add(b), NEW_DBUSER, commit=True)
            
        count = count+1
        if count%1000 == 0:
            print str(count) + '/' + len(fs)

    
if __name__ == "__main__":
    convert()