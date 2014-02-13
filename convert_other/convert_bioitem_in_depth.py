'''
Created on Oct 25, 2013

@author: kpaskov
'''
from sqlalchemy import or_
from convert_other.convert_auxiliary import convert_disambigs, \
    convert_biocon_count, convert_biofact
from convert_utils import create_or_update, create_format_name
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
import logging
import sys

    
# ---------------------Convert------------------------------

def convert(new_session_maker):

    from model_new_schema.bioitem import Domain
    convert_disambigs(new_session_maker, Domain, ['id', 'format_name'], 'BIOITEM', 'DOMAIN', 'convert.domain.disambigs', 2000)
