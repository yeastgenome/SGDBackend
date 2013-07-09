'''
Created on Jul 9, 2013

@author: kpaskov
'''

from model_new_schema.bioconcept import Bioconcept, BioconAncestor, \
    BioconRelation
from model_new_schema.biofact import Biofact
from model_new_schema.go import Go
from model_new_schema.phenotype import Phenotype
from query import session
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.util import with_polymorphic

biocon_type_to_class = {'PHENOTYPE':Phenotype, 'GO':Go}


#Used for go and phenotype pages and go_evidence, phenotype_evidence pages
#Also used for go_graph, go_ontology_graph, and phenotype_ontology_graph.
def get_biocon(biocon_name, biocon_type, print_query=False):
    '''
    get_biocon('DNA_repair', 'GO', print_query=True)
    
    SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_1 
    FROM sprout.biocon LEFT OUTER JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id 
    WHERE sprout.biocon.biocon_type = :biocon_type_1 AND sprout.biocon.name = :name_1
    '''
    query = session.query(with_polymorphic(Bioconcept, [biocon_type_to_class[biocon_type]])).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.format_name==biocon_name)
    biocon = query.first()
    if print_query:
        print query
    return biocon

#Used for go_overview, phenotype_overview, go_evidence, and phenotype_evidence tables
def get_biocon_id(biocon_name, biocon_type, print_query=False):
    '''
    get_biocon_id('DNA_repair', 'GO', print_query=True)
    
    SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.description AS sprout_biocon_description 
    FROM sprout.biocon 
    WHERE sprout.biocon.biocon_type = :biocon_type_1 AND sprout.biocon.name = :name_1
    '''
    query = session.query(Bioconcept).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.format_name==biocon_name)
    biocon = query.first()
    biocon_id = None
    if biocon is not None:
        biocon_id = biocon.id
    if print_query:
        print query
    return biocon_id

def get_biofacts(biocon_type, biocon=None, bioent=None, print_query=False):
    '''
    get_biofacts('GO', biocon=get_biocon('DNA_repair', 'GO'), print_query=True)
    
    SELECT sprout.biofact.biofact_id AS sprout_biofact_biofact_id, sprout.biofact.use_for_graph AS sprout_biofact_use_for_graph, sprout.biofact.bioent_id AS sprout_biofact_bioent_id, sprout.biofact.biocon_id AS sprout_biofact_biocon_id, sprout.biofact.biocon_type AS sprout_biofact_biocon_type, bioent_1.bioent_id AS bioent_1_bioent_id, bioent_1.name AS bioent_1_name, bioent_1.dbxref AS bioent_1_dbxref, bioent_1.bioent_type AS bioent_1_bioent_type, bioent_1.source AS bioent_1_source, bioent_1.secondary_name AS bioent_1_secondary_name, bioent_1.date_created AS bioent_1_date_created, bioent_1.created_by AS bioent_1_created_by, biocon_1.biocon_id AS biocon_1_biocon_id, biocon_1.name AS biocon_1_name, biocon_1.biocon_type AS biocon_1_biocon_type, biocon_1.description AS biocon_1_description 
    FROM sprout.biofact LEFT OUTER JOIN sprout.bioent bioent_1 ON bioent_1.bioent_id = sprout.biofact.bioent_id LEFT OUTER JOIN sprout.biocon biocon_1 ON biocon_1.biocon_id = sprout.biofact.biocon_id 
    WHERE sprout.biofact.biocon_type = :biocon_type_1 AND sprout.biofact.biocon_id = :biocon_id_1
    '''
    if biocon is None and bioent is None:
        raise Exception()
    
    query = session.query(Biofact).options(joinedload('bioentity'), joinedload('bioconcept')).filter(Biofact.biocon_type==biocon_type)
    if bioent is not None:
        query = query.filter(Biofact.bioent_id==bioent.id)
    if biocon is not None:
        query = query.filter(Biofact.biocon_id==biocon.id)
    if print_query:
        print query
    return query.all()

#Used for go_ontology and phenotype_ontology graphs.
def get_biocon_family(biocon, print_query=False):
    '''
    get_biocon_family(get_biocon('DNA_repair', 'GO'), print_query=True)
   
    SELECT sprout.biocon_ancestor.biocon_ancestor_id AS sprout_biocon_ancestor_b_1, sprout.biocon_ancestor.ancestor_biocon_id AS sprout_biocon_ancestor_a_2, sprout.biocon_ancestor.child_biocon_id AS sprout_biocon_ancestor_c_3, sprout.biocon_ancestor.generation AS sprout_biocon_ancestor_g_4, sprout.biocon_ancestor.bioconanc_type AS sprout_biocon_ancestor_b_5, anon_1.sprout_biocon_biocon_id AS anon_1_sprout_biocon_biocon_id, anon_1.sprout_biocon_name AS anon_1_sprout_biocon_name, anon_1.sprout_biocon_biocon_type AS anon_1_sprout_biocon_bio_6, anon_1.sprout_biocon_description AS anon_1_sprout_biocon_des_7, anon_1.sprout_goterm_biocon_id AS anon_1_sprout_goterm_biocon_id, anon_1.sprout_goterm_go_go_id AS anon_1_sprout_goterm_go_go_id, anon_1.sprout_goterm_go_term AS anon_1_sprout_goterm_go_term, anon_1.sprout_goterm_go_aspect AS anon_1_sprout_goterm_go_aspect, anon_1.sprout_goterm_go_definition AS anon_1_sprout_goterm_go__8, anon_1.sprout_goterm_direct_gen_a AS anon_1_sprout_goterm_dir_9 
    FROM sprout.biocon_ancestor LEFT OUTER JOIN (SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_a 
    FROM sprout.biocon LEFT OUTER JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id) anon_1 ON sprout.biocon_ancestor.ancestor_biocon_id = anon_1.sprout_biocon_biocon_id 
    WHERE sprout.biocon_ancestor.child_biocon_id = :child_biocon_id_1

    SELECT sprout.bioconrel.biocon_biocon_id AS sprout_bioconrel_biocon__1, sprout.bioconrel.parent_biocon_id AS sprout_bioconrel_parent__2, sprout.bioconrel.child_biocon_id AS sprout_bioconrel_child_b_3, sprout.bioconrel.relationship_type AS sprout_bioconrel_relatio_4, sprout.bioconrel.bioconrel_type AS sprout_bioconrel_bioconr_5, anon_1.sprout_biocon_biocon_id AS anon_1_sprout_biocon_biocon_id, anon_1.sprout_biocon_name AS anon_1_sprout_biocon_name, anon_1.sprout_biocon_biocon_type AS anon_1_sprout_biocon_bio_6, anon_1.sprout_biocon_description AS anon_1_sprout_biocon_des_7, anon_1.sprout_goterm_biocon_id AS anon_1_sprout_goterm_biocon_id, anon_1.sprout_goterm_go_go_id AS anon_1_sprout_goterm_go_go_id, anon_1.sprout_goterm_go_term AS anon_1_sprout_goterm_go_term, anon_1.sprout_goterm_go_aspect AS anon_1_sprout_goterm_go_aspect, anon_1.sprout_goterm_go_definition AS anon_1_sprout_goterm_go__8, anon_1.sprout_goterm_direct_gen_a AS anon_1_sprout_goterm_dir_9 
    FROM sprout.bioconrel LEFT OUTER JOIN (SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_a 
    FROM sprout.biocon LEFT OUTER JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id) anon_1 ON sprout.bioconrel.child_biocon_id = anon_1.sprout_biocon_biocon_id 
    WHERE sprout.bioconrel.parent_biocon_id = :parent_biocon_id_1
    '''
    biocon_class = biocon_type_to_class[biocon.biocon_type]
    family = set([biocon])
    query1 = session.query(BioconAncestor).options(joinedload(BioconAncestor.ancestor_biocon.of_type(biocon_class))).filter(BioconAncestor.child_id==biocon.id)
    biocon_ancs = query1.all()
    family.update([biocon_anc.ancestor_biocon for biocon_anc in biocon_ancs])
    
    query2 = session.query(BioconRelation).options(joinedload(BioconRelation.child_biocon.of_type(biocon_class))).filter(BioconRelation.parent_id==biocon.id)
    biocon_children = query2.all()
    family.update([biocon_child.child_biocon for biocon_child in biocon_children])
    
    child_ids = set([biocon_child.child_biocon.id for biocon_child in biocon_children])
    all_ids = set([b.id for b in family])
    
    if print_query:
        print query1
        print query2
    return {'family':family, 'child_ids':child_ids, 'all_ids':all_ids}

#Used for go_ontology and phenotype_ontology graphs.
def get_biocon_biocons(biocon_ids, print_query=False):
    '''
    get_biocon_biocons([get_biocon_id('DNA_repair', 'GO')], print_query=True)

    SELECT sprout.bioconrel.biocon_biocon_id AS sprout_bioconrel_biocon__1, sprout.bioconrel.parent_biocon_id AS sprout_bioconrel_parent__2, sprout.bioconrel.child_biocon_id AS sprout_bioconrel_child_b_3, sprout.bioconrel.relationship_type AS sprout_bioconrel_relatio_4, sprout.bioconrel.bioconrel_type AS sprout_bioconrel_bioconr_5 
    FROM sprout.bioconrel 
    WHERE sprout.bioconrel.parent_biocon_id IN (:parent_biocon_id_1)

    SELECT sprout.bioconrel.biocon_biocon_id AS sprout_bioconrel_biocon__1, sprout.bioconrel.parent_biocon_id AS sprout_bioconrel_parent__2, sprout.bioconrel.child_biocon_id AS sprout_bioconrel_child_b_3, sprout.bioconrel.relationship_type AS sprout_bioconrel_relatio_4, sprout.bioconrel.bioconrel_type AS sprout_bioconrel_bioconr_5 
    FROM sprout.bioconrel 
    WHERE sprout.bioconrel.child_biocon_id IN (:child_biocon_id_1)
    '''
    biocon_ids = set(biocon_ids)
    related_biocon_biocons = set()
    
    query1 = session.query(BioconRelation).filter(BioconRelation.parent_id.in_(biocon_ids))
    ancestor_in_list = query1.all()
    related_biocon_biocons.update([biocon_biocon for biocon_biocon in ancestor_in_list if biocon_biocon.child_id in biocon_ids])
    
    query2 = session.query(BioconRelation).filter(BioconRelation.child_id.in_(biocon_ids))
    child_in_list = query2.all()
    related_biocon_biocons.update([biocon_biocon for biocon_biocon in child_in_list if biocon_biocon.parent_id in biocon_ids])
    
    if print_query:
        print query1
        print query2
    return related_biocon_biocons

#Used for go_graph.
def get_related_biofacts(biocon_type, biocon_ids=None, bioent_ids=None, print_query=False):
    '''
    get_related_biofacts([get_biocon_id('DNA_repair', 'GO')], 'GO', print_query=True)
    
    SELECT sprout.biofact.biofact_id AS sprout_biofact_biofact_id, sprout.biofact.use_for_graph AS sprout_biofact_use_for_graph, sprout.biofact.bioent_id AS sprout_biofact_bioent_id, sprout.biofact.biocon_id AS sprout_biofact_biocon_id, sprout.biofact.biocon_type AS sprout_biofact_biocon_type, bioent_1.bioent_id AS bioent_1_bioent_id, bioent_1.name AS bioent_1_name, bioent_1.dbxref AS bioent_1_dbxref, bioent_1.bioent_type AS bioent_1_bioent_type, bioent_1.source AS bioent_1_source, bioent_1.secondary_name AS bioent_1_secondary_name, bioent_1.date_created AS bioent_1_date_created, bioent_1.created_by AS bioent_1_created_by, anon_1.sprout_biocon_biocon_id AS anon_1_sprout_biocon_biocon_id, anon_1.sprout_biocon_name AS anon_1_sprout_biocon_name, anon_1.sprout_biocon_biocon_type AS anon_1_sprout_biocon_bio_1, anon_1.sprout_biocon_description AS anon_1_sprout_biocon_des_2, anon_1.sprout_goterm_biocon_id AS anon_1_sprout_goterm_biocon_id, anon_1.sprout_goterm_go_go_id AS anon_1_sprout_goterm_go_go_id, anon_1.sprout_goterm_go_term AS anon_1_sprout_goterm_go_term, anon_1.sprout_goterm_go_aspect AS anon_1_sprout_goterm_go_aspect, anon_1.sprout_goterm_go_definition AS anon_1_sprout_goterm_go__3, anon_1.sprout_goterm_direct_gen_5 AS anon_1_sprout_goterm_dir_4 
    FROM sprout.biofact LEFT OUTER JOIN sprout.bioent bioent_1 ON bioent_1.bioent_id = sprout.biofact.bioent_id LEFT OUTER JOIN (SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_5 
    FROM sprout.biocon LEFT OUTER JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id) anon_1 ON anon_1.sprout_biocon_biocon_id = sprout.biofact.biocon_id 
    WHERE sprout.biofact.biocon_id IN (:biocon_id_1)
    '''
    biocon_class = biocon_type_to_class[biocon_type]
    query = session.query(Biofact).filter(Biofact.biocon_type==biocon_type).options(joinedload('bioentity'), joinedload(Biofact.bioconcept.of_type(biocon_class)))
    
    if biocon_ids is not None:
        query = query.filter(Biofact.biocon_id.in_(biocon_ids))
    if bioent_ids is not None:
        query = query.filter(Biofact.bioent_id.in_(bioent_ids))
    biofacts = query.all()
    if print_query:
        print query
    return biofacts