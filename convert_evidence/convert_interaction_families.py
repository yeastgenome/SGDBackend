'''
Created on Oct 7, 2013

@author: kpaskov
'''
from convert_aux.interaction_tables import convert_interaction, \
    convert_interaction_family, convert_regulation_family
from convert_utils import set_up_logging, prepare_schema_connection
import model_new_schema

"""
---------------------Convert------------------------------
"""  

def convert(new_session_maker):
    log = set_up_logging('convert.interaction_families')
    
    log.info('begin')

    from model_new_schema.interaction import Physinteractionevidence
    convert_interaction(new_session_maker, Physinteractionevidence, 'PHYSINTERACTION', 'convert.physical_interaction.interaction', 10000, False)
    
    from model_new_schema.interaction import Geninteractionevidence
    convert_interaction(new_session_maker, Geninteractionevidence, 'GENINTERACTION', 'convert.genetic_interaction.interaction', 10000, False)

    convert_interaction_family(new_session_maker, 100)
    
    from model_new_schema.regulation import Regulationevidence
    convert_interaction(new_session_maker, Regulationevidence, 'REGULATION', 'convert.interaction.regulation_interaction', 10000, True)

    convert_regulation_family(new_session_maker, 100)

    log.info('complete')
    
if __name__ == "__main__":
    from convert_all import new_config
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(new_session_maker)   