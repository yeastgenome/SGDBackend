'''
Created on Feb 4, 2013

@author: kpaskov
'''
import model_new_schema

"""
---------------------Cache------------------------------
"""
id_to_bioent = {}
dbxref_id_to_bioent = {}

def feature_to_bioent(feature):
    from model_new_schema.bioentity import Bioentity
    qualifier = None
    attribute = None
    short_description = None
    headline = None
    description = None
    genetic_position = None
    
    ann = feature.annotation
    if ann is not None:
        qualifier = ann.qualifier
        attribute = ann.attribute
        short_description = ann.name_description
        headline = ann.headline
        description = ann.description
        genetic_position = ann.genetic_position
        
    bioent = Bioentity(feature.name, feature_type_to_bioent_type(feature.type), feature.dbxref_id, feature.source, feature.status, feature.gene_name, 
                       qualifier, attribute, short_description, headline, description, genetic_position,
                       bioent_id=feature.id, date_created=feature.date_created, created_by=feature.created_by)
    return bioent

def feature_type_to_bioent_type(feature_type):
    bioent_type = feature_type.upper()
    bioent_type.replace (" ", "_")
    return bioent_type


