'''
Created on Jan 16, 2013

@author: kpaskov
'''
import model_old_schema
from model_old_schema.model import Model as OldModel

import model_new_schema
from model_new_schema.model import Model as NewModel

def convert():
    old_model = OldModel()
    old_model.connect('kpaskov', 'r00tb33r')
    
    new_model = NewModel()
    new_model.connect('kpaskov', 'r00tb33r')
    
    print old_model.execute(model_old_schema.model.get_first(model_old_schema.reference.Reference))
    print new_model.execute(model_new_schema.model.get_first(model_new_schema.bioentity_declarative.Bioentity))
    
if __name__ == "__main__":
    convert()