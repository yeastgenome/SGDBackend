'''
Created on Feb 27, 2013

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

def create_go_id(old_go_id):
    return old_go_id+87636

def create_goevidence_id(old_evidence_id):
    return old_evidence_id+1322521  

def create_go_key(go_term):
    name = go_term.replace(' ', '_')
    name = name.replace('/', '-')
    return (name, 'GO')
                 
abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}
def create_go(old_go):
    from model_new_schema.go import Go as NewGo
    
    new_go = NewGo(create_go_id(old_go.id), old_go.go_go_id, old_go.go_term, 
                   abbrev_to_go_aspect[old_go.go_aspect], old_go.go_definition, 
                   old_go.date_created, old_go.created_by)
    return new_go

def create_synonyms(old_go, key_to_go):
    from model_new_schema.bioconcept import BioconAlias as NewBioconAlias
    biocon_id = key_to_go[create_go_key(old_go.go_term)].id
    new_aliases = [NewBioconAlias(biocon_id, 'GO', synonym.go_synonym, synonym.date_created, synonym.created_by) for synonym in old_go.synonyms]
    return new_aliases

def create_goevidence(old_go_feature, go_ref, key_to_go):
    from model_new_schema.go import Goevidence as NewGoevidence
    evidence_id = create_goevidence_id(go_ref.id)
    reference_id = go_ref.reference_id
    bioent_id = old_go_feature.feature_id
    biocon_id = key_to_go[create_go_key(old_go_feature.go.go_term)].id
    
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

def create_biocon_ancestor(go_path, id_to_old_go, key_to_go):
    from model_new_schema.bioconcept import BioconAncestor as NewBioconAncestor
    ancestor = id_to_old_go[go_path.ancestor_id]
    child = id_to_old_go[go_path.child_id]
        
    ancestor_id = key_to_go[create_go_key(ancestor.go_term)].id
    child_id = key_to_go[create_go_key(child.go_term)].id
    return NewBioconAncestor(ancestor_id, child_id, 'GO_ONTOLOGY', go_path.generation)

     
"""
---------------------Convert------------------------------
"""   

def convert(old_session, new_session):
    from model_old_schema.go import Go as OldGo, GoFeature as OldGoFeature, GoPath as OldGoPath
      
    # Convert goterms
    print 'Go terms'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        old_goterms = old_session.query(OldGo).all()

        convert_goterms(new_session, old_goterms)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
        
    # Convert aliases
    print 'Go term aliases'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        convert_aliases(new_session, old_goterms)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()
        
    # Convert goevidences
    print 'Goevidences'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        old_go_features = old_session.query(OldGoFeature).all()
        
        convert_goevidences(new_session, old_go_features)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close() 
        
    # Update gene counts
    print 'Go term gene counts'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
                
        update_gene_counts(new_session)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close() 
        
    # Convert biocon_relations
    print 'Biocon_relations'            
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        new_session = new_session_maker()
        
        old_go_paths = old_session.query(OldGoPath).filter(OldGoPath.generation==1).all()
        convert_biocon_relations(new_session, old_go_paths, old_goterms)
        ask_to_commit(new_session, start_time)  
    finally:
        old_session.close()
        new_session.close()     
  
    # Convert biocon_ancestors
    # For some reason, when I run this several time, it keeps removing a small number of 
    # biocon_ancestors - not clear why.
    print 'Biocon_ancestors' 
    for i in range(1, 5):       
        print 'Generation ' + str(i)    
        start_time = datetime.datetime.now()
        try:
            old_session = old_session_maker()
            new_session = new_session_maker()
        
            old_go_paths = old_session.query(OldGoPath).filter(OldGoPath.generation==i).all()
            convert_biocon_ancestors(new_session, i, old_go_paths, old_goterms)
            ask_to_commit(new_session, start_time)  
        finally:
            old_session.close()
            new_session.close()     

def convert_goterms(new_session, old_goterms):
    '''
    Convert Goterms
    '''
    from model_new_schema.go import Go as NewGo

    #Cache goterms
    key_to_go = cache(NewGo, new_session)
    
    #Create new goterms if they don't exist, or update the database if they do.
    new_goterms = [create_go(x) for x in old_goterms]
    
    values_to_check = ['go_go_id', 'go_term', 'go_aspect', 'go_definition', 'biocon_type', 'official_name']
    create_or_update_and_remove(new_goterms, key_to_go, values_to_check, new_session)
   
def convert_aliases(new_session, old_goterms):
    '''
    Convert Goterms
    ''' 
    from model_new_schema.go import Go as NewGo
    from model_new_schema.bioconcept import BioconAlias as NewBioconAlias

    #Cache goterm aliases and goterms
    key_to_alias = cache(NewBioconAlias, new_session, biocon_type='GO')
    key_to_go = cache(NewGo, new_session)    
    
    new_goterm_aliases = []
    for old_goterm in old_goterms:
        new_goterm_aliases.extend(create_synonyms(old_goterm, key_to_go))
        
    #Create new aliases if they don't exist of update the dataset if they do.
    values_to_check = ['biocon_type', 'date_created', 'created_by']
    create_or_update_and_remove(new_goterm_aliases, key_to_alias, values_to_check, new_session)
    
    
def convert_goevidences(new_session, old_go_features):
    '''
    Convert Goterms
    '''
    from model_new_schema.go import Goevidence as NewGoevidence, Go as NewGo
    
    #Cache goevidences and goterms
    key_to_goevidence = cache(NewGoevidence, new_session)
    key_to_go = cache(NewGo, new_session)
    
    #Create new goevidences if they don't exist, or update the database if they do.
    new_evidences = []
    values_to_check = ['go_evidence', 'annotation_type', 'date_last_reviewed', 'qualifier',
                       'bioent_id', 'biocon_id', 'experiment_type', 'reference_id', 'evidence_type',
                       'strain_id', 'source', 'date_created', 'created_by']
    for old_go_feature in old_go_features: 
        new_evidences.extend([create_goevidence(old_go_feature, x, key_to_go) for x in old_go_feature.go_refs])
    create_or_update_and_remove(new_evidences, key_to_goevidence, values_to_check, new_session)
    
def update_gene_counts(new_session):
    '''
    Update goterm gene counts
    '''
    from model_new_schema.go import Goevidence as NewGoevidence, Go as NewGo

    goterms = new_session.query(NewGo).all()
    goevidences = new_session.query(NewGoevidence).all()
    biocon_id_to_bioent_ids = {}
    
    for goterm in goterms:
        biocon_id_to_bioent_ids[goterm.id] = set()
        
    for goevidence in goevidences:
        biocon_id_to_bioent_ids[goevidence.biocon_id].add(goevidence.bioent_id)
        
    num_changed = 0
    for goterm in goterms:
        count = len(biocon_id_to_bioent_ids[goterm.id])
        if count != goterm.direct_gene_count:
            goterm.direct_gene_count = count
            num_changed = num_changed + 1
    print 'In total ' + str(num_changed) + ' changed.'
            
    
def convert_biocon_relations(new_session, old_go_paths, old_goterms):
    '''
    Convert Biocon_relations
    '''
    from model_new_schema.bioconcept import BioconRelation as NewBioconRelation
    from model_new_schema.go import Go as NewGo
    
    #Cache biocon_relations and goterms
    key_to_biocon_relations = cache(NewBioconRelation, new_session, bioconrel_type='GO_ONTOLOGY')
    key_to_go = cache(NewGo, new_session)
    
    id_to_old_go = dict([(x.id, x) for x in old_goterms])
    
    #Create new biocon_relations if they don't exist, or update the database if they do.
    new_biocon_relations = filter(None, [create_biocon_relation(x, id_to_old_go, key_to_go) for x in old_go_paths])
    create_or_update_and_remove(new_biocon_relations, key_to_biocon_relations, [], new_session) 
    
def convert_biocon_ancestors(new_session, generation, old_go_paths, old_goterms):
    '''
    Convert Biocon_ancestors
    '''
    from model_new_schema.bioconcept import BioconAncestor as NewBioconAncestor
    from model_new_schema.go import Go as NewGo
    
    #Cache biocon_ancestors and goterms
    key_to_biocon_ancestors = cache(NewBioconAncestor, new_session, bioconanc_type='GO_ONTOLOGY', generation=generation)
    key_to_go = cache(NewGo, new_session)
    
    id_to_old_go = dict([(x.id, x) for x in old_goterms])
    
    #Create new biocon_ancestors if they don't exist, or update the database if they do.
    new_biocon_ancestors = [create_biocon_ancestor(x, id_to_old_go, key_to_go) for x in old_go_paths]
    create_or_update_and_remove(new_biocon_ancestors, key_to_biocon_ancestors, [], new_session) 
   
if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)
            
    

    
            
        
            
            
            
            
            