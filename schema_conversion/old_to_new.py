'''
Created on Feb 4, 2013

@author: kpaskov
'''

def feature_to_bioent(feature):
    from model_new_schema.bioentity import Bioentity

    bioent = Bioentity(feature.name, feature_type_to_bioent_type(feature.type), feature.dbxref_id, feature.source, feature.status, 
                       bioent_id=feature.id, date_created=feature.date_created, created_by=feature.created_by)
    return bioent

def feature_type_to_bioent_type(feature_type):
    bioent_type = feature_type.upper()
    bioent_type.replace (" ", "_")
    return bioent_type

def interaction_to_biorelation(interaction):
    