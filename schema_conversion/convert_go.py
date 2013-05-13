'''
Created on Feb 27, 2013

@author: kpaskov
'''
from model_old_schema.config import DBUSER as OLD_DBUSER
from schema_conversion import check_values, cache, create_or_update, \
    add_or_check
from schema_conversion.old_to_new_bioentity import id_to_bioent
from schema_conversion.output_manager import OutputCreator
import model_old_schema


"""
---------------------Cache------------------------------
"""

id_to_biocon = {}
id_to_evidence = {}
id_to_biocon_biocon = {}
id_to_biocon_ancestor = {}
tuple_to_bioent_biocon = {}

def cache_biocon(session, biocon_type):
    from model_new_schema.bioconcept import Bioconcept as NewBiocon
    if biocon_type is None:
        new_entries = dict([(biocon.id, biocon) for biocon in session.query(NewBiocon).all()])
    else:
        new_entries = dict([(biocon.id, biocon) for biocon in session.query(NewBiocon).filter_by(biocon_type=biocon_type).all()])
    id_to_biocon.update(new_entries)
    
def cache_bioent_biocon(session, biocon_type):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    key_extractor = lambda x: (x.bioent_id, x.biocon_id)
    if biocon_type is None:
        new_entries = dict([(key_extractor(bioent_biocon), bioent_biocon) for bioent_biocon in session.query(NewBioentBiocon).all()])
    else:
        new_entries = dict([(key_extractor(bioent_biocon), bioent_biocon) for bioent_biocon in session.query(NewBioentBiocon).filter_by(biocon_type=biocon_type).all()])
    tuple_to_bioent_biocon.update(new_entries)
    
def cache_evidence(session, evidence_type):
    from model_new_schema.evidence import Evidence as NewEvidence
    if evidence_type is None:
        new_entries = dict([(goevidence.id, goevidence) for goevidence in session.query(NewEvidence).all()])
    else:
        new_entries = dict([(goevidence.id, goevidence) for goevidence in session.query(NewEvidence).filter_by(evidence_type=evidence_type).all()])
    id_to_evidence.update(new_entries)
             

"""
---------------------Create------------------------------
"""

def create_bioent_biocon_name(bioent, biocon):
    return bioent.official_name + '---' + biocon.official_name

def create_go_id(old_go_id):
    return old_go_id+87636

def create_goevidence_id(old_evidence_id):
    return old_evidence_id+1322521  
                 
abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}
def create_go(old_go):
    from model_new_schema.bioconcept import Go as NewGo
    
    new_go = NewGo(old_go.go_go_id, old_go.go_term, abbrev_to_go_aspect[old_go.go_aspect], old_go.go_definition, 
                   biocon_id=create_go_id(old_go.id), date_created=old_go.date_created, created_by=old_go.created_by)
    return new_go

def create_go_bioent_biocon(old_go_feature):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    bioent_id = old_go_feature.feature_id
    biocon_id = create_go_id(old_go_feature.go_id)
        
    bioent = id_to_bioent[bioent_id]
    biocon = id_to_biocon[biocon_id]
    name = create_bioent_biocon_name(bioent, biocon)
    return NewBioentBiocon(bioent_id, biocon_id, name, biocon.biocon_type)

def create_goevidence(old_go_feature, go_ref):
    from model_new_schema.evidence import Goevidence as NewGoevidence
    bioent_id = old_go_feature.feature_id
    biocon_id = create_go_id(old_go_feature.go_id)
    bioent_biocon_id = tuple_to_bioent_biocon[(bioent_id, biocon_id)].id
    evidence_id = create_goevidence_id(go_ref.id)
    qualifier = None
    if go_ref.go_qualifier is not None:
        qualifier = go_ref.qualifier
    return NewGoevidence(bioent_biocon_id, go_ref.reference_id, old_go_feature.go_evidence, old_go_feature.annotation_type, old_go_feature.source,
                                qualifier, old_go_feature.date_last_reviewed, 
                                evidence_id=evidence_id, date_created=go_ref.date_created, created_by=go_ref.created_by)
    
def create_go_biocon_biocon(go_path):
    from model_new_schema.bioconcept import BioconBiocon as NewBioconBiocon
    if go_path.generation == 1:
        parent_id = go_path.ancestor_id
        child_id = go_path.child_id
        relationship_type = go_path.relationship_type
        return NewBioconBiocon(parent_id, child_id, relationship_type, biocon_biocon_id=go_path.id)
    else:
        return None

def create_go_biocon_ancestor(go_path):
    from model_new_schema.bioconcept import BioconAncestor as NewBioconAncestor
    ancestor_id = go_path.ancestor_id
    child_id = go_path.child_id
    return NewBioconAncestor(ancestor_id, child_id, biocon_ancestor_id=go_path.id)


     
"""
---------------------Convert------------------------------
"""   

def convert_go(old_session, new_session):
    from model_old_schema.go import Go as OldGo, GoFeature as OldGoFeature

    from model_new_schema.bioentity import Bioentity as NewBioentity
      
    output_creator = OutputCreator()

    #Cache bioents
    cache(NewBioentity, id_to_bioent, lambda x: x.id, new_session, output_creator, 'bioent')
     
    #Cache go_biocons
    cache_biocon(new_session, 'GO')
    output_creator.cached('biocon')

    #Create new go_biocons if they don't exist, or update the database if they do.
    old_objs = old_session.query(OldGo).all()
    key_maker = lambda x: x.id
    values_to_check = ['go_go_id', 'go_term', 'go_aspect', 'go_definition']
    create_or_update(old_objs, id_to_biocon, create_go, key_maker, values_to_check, new_session, output_creator)

    #Cache bioent_biocons
    cache_bioent_biocon(new_session, 'GO')
    output_creator.cached('bioent_biocon')
    
    #Create new bioent_biocons if they don't exist, or update the database if they do.
    old_go_features = old_session.query(OldGoFeature).all()
    key_maker = lambda x: (x.bioent_id, x.biocon_id)
    values_to_check = ['bioent_id', 'biocon_id', 'official_name', 'biocon_type']
    create_or_update(old_go_features, tuple_to_bioent_biocon, create_go_bioent_biocon, key_maker, values_to_check, new_session, output_creator)
    
#    #Cache goevidences
#    cache_evidence(session, 'GO_EVIDENCE')
#    output_creator.cached('goevidence')
#    
#    #Create new goevidences if they don't exist, or update the database if they do.
#    key_maker = lambda x: x.id
#    values_to_check = ['bioent_biocon_id', 'go_evidence', 'annotation_type', 'source', 'date_last_reviewed', 'qualifier']
#    for old_go_feature in old_go_features: 
#        for go_ref in old_go_feature.go_refs:
#            new_evidence = create_goevidence(old_go_feature, go_ref)
#            add_or_check(new_evidence, id_to_evidence, key_maker, values_to_check, session, output_creator, 'goevidence', [check_evidence])
#    output_creator.finished('goevidence')            
#    
#    use_in_graph = set()
#    for goevidence in id_to_evidence.values():
#        if goevidence.evidence_type == 'GO_EVIDENCE' and goevidence.annotation_type != 'computational':
#            use_in_graph.add(goevidence.bioent_biocon)
#    
#    #Set use_in_graph value for all bioent_biocons 
#    changed = 0;
#    for bioent_biocon in tuple_to_bioent_biocon.values():
#        if bioent_biocon.use_in_graph == 'Y' and bioent_biocon not in use_in_graph:
#            bioent_biocon.use_in_graph = 'N'
#            changed = changed + 1
#        elif bioent_biocon.use_in_graph == 'N' and bioent_biocon in use_in_graph:
#            bioent_biocon.use_in_graph = 'Y'
#            changed = changed + 1
#    print 'In total ' + str(changed) + ' bioent_biocons use_in_graph changed.'

#    #Cache biocon_biocons
#    key_maker = lambda x: x.id
#    cache(NewBioconBiocon, id_to_biocon_biocon, key_maker, session, output_creator, 'biocon_biocon')
#    
#    #Create new biocon_biocons if they don't exist, or update the database if they do.
#    old_go_paths = old_model.execute(model_old_schema.model.get(OldGoPath), OLD_DBUSER)
#    values_to_check = ['parent_biocon_id', 'child_biocon_id', 'relationship_type']
#    for old_go_path in old_go_paths: 
#        new_biocon_biocon = create_go_biocon_biocon(old_go_path)
#        add_or_check(new_biocon_biocon, id_to_biocon_biocon, key_maker, values_to_check, session, output_creator, 'biocon_biocon')
#    output_creator.finished('biocon_biocon')  
#    
#    #Cache biocon_ancestors
#    key_maker = lambda x: x.id
#    cache(NewBioconAncestor, id_to_biocon_ancestor, key_maker, session, output_creator, 'biocon_ancestor')
#    
#    #Create new biocon_ancestors if they don't exist, or update the database if they do.
#    values_to_check = ['ancestor_biocon_id', 'child_biocon_id']
#    for old_go_path in old_go_paths: 
#        new_biocon_ancestor = create_go_biocon_ancestor(old_go_path)
#        add_or_check(new_biocon_ancestor, id_to_biocon_ancestor, key_maker, values_to_check, session, output_creator, 'biocon_ancestor')
#    output_creator.finished('biocon_ancestor')      
   
    
            
    

    
            
        
            
            
            
            
            