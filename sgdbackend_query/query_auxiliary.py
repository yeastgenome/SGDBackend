'''
Created on Oct 26, 2013

@author: kpaskov
'''

from model_new_schema.auxiliary import Interaction, BioentityReference, Biofact, \
    Locustabs, Disambig
from sgdbackend_query import session
from sqlalchemy.sql.expression import or_

#Used for interaction_overview_table.
def get_interactions(interaction_type, bioent_id, print_query=False):
    query = session.query(Interaction).filter(
                                or_(Interaction.bioentity1_id == bioent_id, 
                                    Interaction.bioentity2_id == bioent_id)).filter(
                                Interaction.class_type==interaction_type)                                                                                    
    interactions = query.all()
    if print_query:
        print query
    return interactions

#Used for literature overview
def get_bioentity_references(class_type, bioent_id=None, reference_id=None, bioent_ids=None, reference_ids=None, print_query=False):
    query = session.query(BioentityReference).filter(BioentityReference.class_type == class_type)
    if bioent_id is not None:
        query = query.filter(BioentityReference.bioentity_id == bioent_id)
    if reference_id is not None:
        query = query.filter(BioentityReference.reference_id == reference_id)
    if bioent_ids is not None:
        query = query.filter(BioentityReference.bioentity_id.in_(bioent_ids))
    if reference_ids is not None:
        query = query.filter(BioentityReference.reference_id.in_(reference_ids))
    bioent_refs = query.all()
    if print_query:
        print query
    return bioent_refs

def get_biofacts(biocon_type, biocon_id=None, bioent_id=None, print_query=False):
    '''
    get_biofacts('GO', biocon=get_biocon('DNA_repair', 'GO'), print_query=True)
    
    SELECT sprout.biofact.biofact_id AS sprout_biofact_biofact_id, sprout.biofact.use_for_graph AS sprout_biofact_use_for_graph, sprout.biofact.bioent_id AS sprout_biofact_bioent_id, sprout.biofact.biocon_id AS sprout_biofact_biocon_id, sprout.biofact.biocon_type AS sprout_biofact_biocon_type, bioent_1.bioent_id AS bioent_1_bioent_id, bioent_1.name AS bioent_1_name, bioent_1.dbxref AS bioent_1_dbxref, bioent_1.bioent_type AS bioent_1_bioent_type, bioent_1.source AS bioent_1_source, bioent_1.secondary_name AS bioent_1_secondary_name, bioent_1.date_created AS bioent_1_date_created, bioent_1.created_by AS bioent_1_created_by, biocon_1.biocon_id AS biocon_1_biocon_id, biocon_1.name AS biocon_1_name, biocon_1.biocon_type AS biocon_1_biocon_type, biocon_1.description AS biocon_1_description 
    FROM sprout.biofact LEFT OUTER JOIN sprout.bioent bioent_1 ON bioent_1.bioent_id = sprout.biofact.bioent_id LEFT OUTER JOIN sprout.biocon biocon_1 ON biocon_1.biocon_id = sprout.biofact.biocon_id 
    WHERE sprout.biofact.biocon_type = :biocon_type_1 AND sprout.biofact.biocon_id = :biocon_id_1
    '''
    
    query = session.query(Biofact).filter(Biofact.bioconcept_class_type==biocon_type)
    if bioent_id is not None:
        query = query.filter(Biofact.bioentity_id==bioent_id)
    if biocon_id is not None:
        query = query.filter(Biofact.bioconcept_id==biocon_id)
    if print_query:
        print query
    return query.all()

#Used to determine tabs on all pages.
def query_locustabs(bioentity_id, print_query=False):
    query = session.query(Locustabs).filter(Locustabs.id==bioentity_id)
    if print_query:
        print query
    return query.first()

def get_disambigs(min_id, max_id, print_query=False):
    query = session.query(Disambig)
    if min_id is not None:
        query = query.filter(Disambig.id >= min_id)
    if max_id is not None:
        query = query.filter(Disambig.id < max_id)
    disambigs = query.all()
    if print_query:
        print_query
    return disambigs