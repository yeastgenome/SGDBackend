'''
Created on Oct 28, 2013

@author: kpaskov
'''
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, CLOB

data_table_names = ['binding_site_details', 
                    'go_overview', 'go_details_bioent', 'go_details_biocon', 'go_ontology_graph', 
                    'interaction_overview', 'interaction_details', 'interaction_graph', 'interaction_resources',
                    'literature_overview', 'literature_details', 'literature_graph',
                    'phenotype_overview', 'phenotype_details_bioent', 'phenotype_details_biocon', 'phenotype_ontology_graph',
                    'protein_domain_details',
                    'regulation_overview', 'regulation_details', 'regulation_graph', 'regulation_target_enrich']
data_classes = {}

def get_id_col_name(tablename):
    if tablename.endswith('biocon') or tablename == 'go_ontology_graph' or tablename == 'phenotype_ontology_graph':
        return 'bioconcept_id'
    else:
        return 'bioentity_id'

def create_data_classes():
    for table_name in data_table_names:
        id_col_name = get_id_col_name(table_name)
        if id_col_name is not None:
            data_classes[table_name] = perf_factory(table_name, id_col_name)

def perf_factory(tablename, id_col_name) :
    from model_perf_schema import EqualityByIDMixin, Base
    class NewClass(Base, EqualityByIDMixin):
        __tablename__ = tablename
        
        id = Column(id_col_name, Integer, primary_key=True)
        json = Column('json', CLOB)
                    
        def __init__(self, obj_id, json):
            self.id = obj_id
            self.json = json
    
    NewClass.__name__ = tablename.title().replace('_', '')
    return NewClass