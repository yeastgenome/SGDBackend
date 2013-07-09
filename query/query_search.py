'''
Created on Jul 9, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.reference import Reference
from model_new_schema.search import Typeahead
from query import session
from sqlalchemy.orm import joinedload

#Used for search_results_table.
def search(search_strs, bio_type, print_query=False): 
    '''
    search(['ACT'], None, print_query=True)

    SELECT sprout.typeahead3.typeahead_id AS sprout_typeahead3_typeahead_id, sprout.typeahead3.name AS sprout_typeahead3_name, sprout.typeahead3.full_name AS sprout_typeahead3_full_name, sprout.typeahead3.bio_type AS sprout_typeahead3_bio_type, sprout.typeahead3.bio_id AS sprout_typeahead3_bio_id, sprout.typeahead3.source AS sprout_typeahead3_source, sprout.typeahead3.use_for_typeahead AS sprout_typeahead3_use_fo_1, sprout.typeahead3.use_for_search AS sprout_typeahead3_use_fo_2 
    FROM sprout.typeahead3 
    WHERE sprout.typeahead3.name = :name_1
    '''  
    for search_str in search_strs: 
        query = session.query(Typeahead).filter(Typeahead.name == search_str.lower()) 
        if bio_type != None:
            query = query.filter(Typeahead.bio_type == bio_type)          
        search_results = query.all() 
        
        if print_query:
            print query  
        return search_results

#Used for search_results_table.
def get_objects(search_results, print_query=False):
    '''
    get_objects(search(['ACT'], None), print_query=True)
    
    None
    
    SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.description AS sprout_biocon_description 
    FROM sprout.biocon 
    WHERE sprout.biocon.biocon_id IN (:biocon_id_1, :biocon_id_2, :biocon_id_3, :biocon_id_4, :biocon_id_5, :biocon_id_6, :biocon_id_7, :biocon_id_8, :biocon_id_9, :biocon_id_10)
    
    None
    '''
    tuple_to_obj = dict()
    bioent_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type == 'LOCUS']
    biocon_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type in {'PHENOTYPE', 'GO'}]
    reference_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type == 'REFERENCE']    
    
    query1 = None
    query2 = None
    query3 = None
    if len(bioent_ids) > 0:
        query1 = session.query(Bioentity).options(joinedload('bioentaliases')).filter(Bioentity.id.in_(bioent_ids))
        bioents = query1.all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in bioents])
    
    if len(biocon_ids) > 0:
        query2 = session.query(Bioconcept).filter(Bioconcept.id.in_(biocon_ids))
        biocons = query2.all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in biocons])
     
    if len(reference_ids) > 0:   
        query3 = session.query(Reference).filter(Reference.id.in_(reference_ids))
        refs = query3.all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in refs])
        
    ordered_objects = []    
    for result in search_results:
        ordered_objects.append(tuple_to_obj[(result.bio_type, result.bio_id)])
        
    if print_query:
        print query1
        print query2
        print query3
    return ordered_objects