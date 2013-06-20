'''
Created on May 28, 2013

@author: kpaskov
'''
from schema_conversion import create_or_update_and_remove, cache_by_key

def update_biocon_gene_counts(new_session, biocon_cls, evidence_cls):
    '''
    Update goterm gene counts
    '''

    biocons = new_session.query(biocon_cls).all()
    evidences = new_session.query(evidence_cls).all()
    biocon_id_to_bioent_ids = {}
    
    for biocon in biocons:
        biocon_id_to_bioent_ids[biocon.id] = set()
        
    for evidence in evidences:
        biocon_id_to_bioent_ids[evidence.biocon_id].add(evidence.bioent_id)
        
    num_changed = 0
    for biocon in biocons:
        count = len(biocon_id_to_bioent_ids[biocon.id])
        if count != biocon.direct_gene_count:
            biocon.direct_gene_count = count
            num_changed = num_changed + 1
    print 'In total ' + str(num_changed) + ' changed.'
    
def update_biorel_evidence_counts(new_session, biorel_cls, evidence_cls):
    biorels = new_session.query(biorel_cls).all()
    evidences = new_session.query(evidence_cls).all()
    biorel_id_to_evidence_count = {}
    
    for biorel in biorels:
        biorel_id_to_evidence_count[biorel.id] = 0
        
    for evidence in evidences:
        biorel_id_to_evidence_count[evidence.biorel_id] = biorel_id_to_evidence_count[evidence.biorel_id]+1
        
    num_changed = 0
    for biorel in biorels:
        count = biorel_id_to_evidence_count[biorel.id]
        if count != biorel.evidence_count:
            biorel.evidence_count = count
            num_changed = num_changed + 1
    print 'In total ' + str(num_changed) + ' changed.'

def convert_biocon_ancestors(new_session, bioconrel_type, num_generations):
    from model_new_schema.bioconcept import BioconRelation as NewBioconRelation, BioconAncestor as NewBioconAncestor
    
    #Cache biocon_relations and biocon_ancestors
    key_to_biocon_relations = cache_by_key(NewBioconRelation, new_session, bioconrel_type=bioconrel_type)
    
    child_to_parents = {}
    for biocon_relation in key_to_biocon_relations.values():
        child_id = biocon_relation.child_id
        parent_id = biocon_relation.parent_id
        if child_id not in child_to_parents:
            child_to_parents[child_id] = set()
        if parent_id not in child_to_parents:
            child_to_parents[parent_id] = set()
            
        child_to_parents[child_id].add(parent_id)

    child_to_ancestors = dict([(child_id, [parent_ids]) for child_id, parent_ids in child_to_parents.iteritems()])
    for i in range(2, num_generations):
        for ancestor_ids in child_to_ancestors.values():
            last_generation = ancestor_ids[-1]
            new_generation = set()
            [new_generation.update(child_to_parents[child_id]) for child_id in last_generation]
            ancestor_ids.append(new_generation)
        
    
    for generation in range(1, num_generations):
        print 'Generation ' + str(generation)
        key_to_biocon_ancestors = cache_by_key(NewBioconAncestor, new_session, bioconanc_type=bioconrel_type, generation=generation)
        new_biocon_ancestors = []    

        for child_id, all_ancestor_ids in child_to_ancestors.iteritems():
            this_generation = all_ancestor_ids[generation-1]
            new_biocon_ancestors.extend([NewBioconAncestor(ancestor_id, child_id, bioconrel_type, generation) for ancestor_id in this_generation])
        create_or_update_and_remove(new_biocon_ancestors, key_to_biocon_ancestors, [], new_session) 
        
