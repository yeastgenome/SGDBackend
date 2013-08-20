'''
Created on Jul 9, 2013

@author: kpaskov
'''

from model_new_schema.auxiliary import Interaction, InteractionFamily
from sgdbackend_query import session
from sqlalchemy.sql.expression import or_

#Used for interaction_overview_table.
def get_interactions(interaction_type, bioent_id, print_query=False):
    query = session.query(Interaction).filter(
                                or_(Interaction.bioent1_id == bioent_id, 
                                    Interaction.bioent2_id == bioent_id)).filter(
                                Interaction.interaction_type==interaction_type)                                                                                    
    interactions = query.all()
    if print_query:
        print query
    return interactions

#Used for interaction graph
def get_interaction_family(bioent_id, print_query=False):
    query = session.query(InteractionFamily).filter(
                                InteractionFamily.bioent_id==bioent_id)
    interactions = query.all()
    if print_query:
        print query
    return interactions