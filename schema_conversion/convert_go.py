'''
Created on Feb 27, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, \
    prepare_schema_connection, cache_by_key, cache_by_id, create_format_name, \
    execute_conversion
from schema_conversion.auxillary_tables import update_biocon_gene_counts, \
    convert_biocon_ancestors
from schema_conversion.output_manager import write_to_output_file
import model_new_schema
import model_old_schema


"""
---------------------Create------------------------------
"""

def create_go_id(old_go_id):
    return old_go_id+87636

def create_goevidence_id(old_evidence_id):
    return old_evidence_id+1400000  

def create_go_key(go_term):
    name = go_term.replace(' ', '_')
    name = name.replace('/', '-')
    return (name, 'GO')
                 
abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}
def create_go(old_go):
    from model_new_schema.go import Go as NewGo
    
    display_name = old_go.go_term
    format_name = create_format_name(display_name)
    new_go = NewGo(create_go_id(old_go.id), display_name, format_name, old_go.go_definition,
                   old_go.go_go_id, abbrev_to_go_aspect[old_go.go_aspect],  
                   old_go.date_created, old_go.created_by)
    return new_go

def create_synonyms(old_go, key_to_go):
    from model_new_schema.bioconcept import BioconAlias as NewBioconAlias
    go_key = create_go_key(old_go.go_term)
    if go_key not in key_to_go:
        print 'GO term does not exist. ' + str(go_key)
        return []
    biocon_id = key_to_go[go_key].id
    
    new_aliases = [NewBioconAlias(synonym.go_synonym, biocon_id, 'GO', synonym.date_created, synonym.created_by) for synonym in old_go.synonyms]
    return new_aliases

def create_goevidence(old_go_feature, go_ref, key_to_go, id_to_reference, id_to_bioent):
    from model_new_schema.go import Goevidence as NewGoevidence
    evidence_id = create_goevidence_id(go_ref.id)
    reference_id = go_ref.reference_id
    if reference_id not in id_to_reference:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    bioent_id = old_go_feature.feature_id
    if bioent_id not in id_to_bioent:
        print 'Bioentity does not exist. ' + str(bioent_id)
        return None
    
    go_key = create_go_key(old_go_feature.go.go_term)
    if go_key not in key_to_go:
        print 'Go term does not exist. ' + str(go_key)
        return None
    biocon_id = key_to_go[go_key].id
    
    qualifier = None
    if go_ref.go_qualifier is not None and go_ref.qualifier is not None:
        qualifier = go_ref.qualifier
    return NewGoevidence(evidence_id, reference_id, old_go_feature.source,
                                old_go_feature.go_evidence, old_go_feature.annotation_type, qualifier, old_go_feature.date_last_reviewed, 
                                bioent_id, biocon_id, go_ref.date_created, go_ref.created_by)
    return None

def create_biocon_relation(go_path, id_to_old_go, key_to_go):
    from model_new_schema.bioconcept import BioconRelation as NewBioconRelation
    if go_path.generation == 1:
        ancestor = id_to_old_go[go_path.ancestor_id]
        child = id_to_old_go[go_path.child_id]
        
        parent_id = key_to_go[create_go_key(ancestor.go_term)].id
        child_id = key_to_go[create_go_key(child.go_term)].id
        relationship_type = go_path.relationship_type
        return NewBioconRelation(parent_id, child_id, 'GO_ONTOLOGY', relationship_type)
    else:
        return None
     
"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker, ask):
    from model_old_schema.go import Go as OldGo, GoFeature as OldGoFeature, GoPath as OldGoPath
    from model_new_schema.go import Go as NewGo, Goevidence as NewGoevidence
      
    # Convert goterms
    write_to_output_file( 'Go terms')
    execute_conversion(convert_goterms, old_session_maker, new_session_maker, ask,
                       old_goterms=lambda old_session: old_session.query(OldGo).all())
        
    # Convert aliases
    write_to_output_file( 'Go term aliases')
    execute_conversion(convert_aliases, old_session_maker, new_session_maker, ask,
                       old_goterms=lambda old_session: old_session.query(OldGo).all())
        
    # Convert goevidences
    write_to_output_file('Goevidences')
    execute_conversion(convert_goevidences, old_session_maker, new_session_maker, ask,
                       old_go_features=lambda old_session: old_session.query(OldGoFeature).all())
        
    # Convert biocon_relations
    write_to_output_file( 'Biocon_relations')  
    execute_conversion(convert_biocon_relations, old_session_maker, new_session_maker, ask,
                       old_go_paths=lambda old_session:old_session.query(OldGoPath).filter(OldGoPath.generation==1).all(),
                       old_goterms=lambda old_session:old_session.query(OldGo).all())     
        
    # Update gene counts
    write_to_output_file( 'Go term gene counts')
    execute_conversion(update_biocon_gene_counts, old_session_maker, new_session_maker, ask,
                       biocon_cls=lambda old_session:NewGo,
                       evidence_cls=lambda old_session:NewGoevidence)   
  
    # Convert biocon_ancestors
    # For some reason, when I run this several time, it keeps removing a small number of 
    # biocon_ancestors - not clear why.
    write_to_output_file( 'Biocon_ancestors' )
    execute_conversion(convert_biocon_ancestors, old_session_maker, new_session_maker, ask,
                       bioconrel_type=lambda old_session:'GO_ONTOLOGY',
                       num_generations=lambda old_session:5)   

def convert_goterms(new_session, old_goterms):
    '''
    Convert Goterms
    '''
    from model_new_schema.go import Go as NewGo

    #Cache goterms
    key_to_go = cache_by_key(NewGo, new_session)
    
    #Create new goterms if they don't exist, or update the database if they do.
    new_goterms = [create_go(x) for x in old_goterms]
    
    values_to_check = ['go_go_id', 'go_aspect', 'biocon_type', 'display_name', 'format_name', 'description', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_goterms, key_to_go, values_to_check, new_session)
    return success
   
def convert_aliases(new_session, old_goterms):
    '''
    Convert Goterms
    ''' 
    from model_new_schema.go import Go as NewGo
    from model_new_schema.bioconcept import BioconAlias as NewBioconAlias

    #Cache goterm aliases and goterms
    key_to_alias = cache_by_key(NewBioconAlias, new_session, biocon_type='GO')
    key_to_go = cache_by_key(NewGo, new_session)    
    
    new_goterm_aliases = []
    for old_goterm in old_goterms:
        new_goterm_aliases.extend(create_synonyms(old_goterm, key_to_go))
        
    #Create new aliases if they don't exist of update the dataset if they do.
    values_to_check = ['biocon_type', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_goterm_aliases, key_to_alias, values_to_check, new_session)
    return success
    
def convert_goevidences(new_session, old_go_features):
    '''
    Convert Goterms
    '''
    from model_new_schema.go import Goevidence as NewGoevidence, Go as NewGo
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.reference import Reference as NewReference
    
    #Cache goevidences and goterms
    key_to_goevidence = cache_by_key(NewGoevidence, new_session)
    key_to_go = cache_by_key(NewGo, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    id_to_bioent = cache_by_id(NewBioentity, new_session)
            
    #Create new goevidences if they don't exist, or update the database if they do.
    new_evidences = []
    values_to_check = ['go_evidence', 'annotation_type', 'date_last_reviewed', 'qualifier',
                       'bioent_id', 'biocon_id', 'experiment_id', 'reference_id', 'evidence_type',
                       'strain_id', 'source', 'date_created', 'created_by']
    for old_go_feature in old_go_features: 
        new_evidences.extend([create_goevidence(old_go_feature, x, key_to_go, id_to_reference, id_to_bioent) for x in old_go_feature.go_refs])
    
    success = create_or_update_and_remove(new_evidences, key_to_goevidence, values_to_check, new_session)
    return success      
    
def convert_biocon_relations(new_session, old_go_paths, old_goterms):
    '''
    Convert Biocon_relations
    '''
    from model_new_schema.bioconcept import BioconRelation as NewBioconRelation
    from model_new_schema.go import Go as NewGo
    
    #Cache biocon_relations and goterms
    key_to_biocon_relations = cache_by_key(NewBioconRelation, new_session, bioconrel_type='GO_ONTOLOGY')
    key_to_go = cache_by_key(NewGo, new_session)
    
    id_to_old_go = dict([(x.id, x) for x in old_goterms])
    
    #Create new biocon_relations if they don't exist, or update the database if they do.
    new_biocon_relations = filter(None, [create_biocon_relation(x, id_to_old_go, key_to_go) for x in old_go_paths])
    success = create_or_update_and_remove(new_biocon_relations, key_to_biocon_relations, [], new_session) 
    return success
            
if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker, False)
    

    
            
        
            
            
            
            
            