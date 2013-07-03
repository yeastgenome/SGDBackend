'''
Created on Jul 3, 2013

@author: kpaskov
'''

from email.mime.text import MIMEText
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import prepare_schema_connection, convert_reference, \
    convert_bioentity, convert_evelements
from schema_conversion.output_manager import output_file, write_to_output_file
import model_new_schema
import model_old_schema
import smtplib
import sys

def send_output_email():

    fp = open(output_file, 'rb')
    # Create a text/plain message
    msg = MIMEText(fp.read())
    fp.close()

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = 'Schema Conversion'
    msg['From'] = 'kpaskov@stanford.edu'
    msg['To'] = 'kpaskov@stanford.edu'

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('smtp.stanford.edu')
    s.set_debuglevel(1) 
    s.ehlo() 
    s.starttls() 
    s.ehlo() 
    s.sendmail('kpaskov@stanford.edu', ['kpaskov@stanford.edu'], msg.as_string())
    s.quit()

if __name__ == "__main__":
    f = open(output_file, 'w')
    f.close()

    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    
    write_to_output_file( '----------------------------------------')
    write_to_output_file( 'Convert Bioentities')
    write_to_output_file( '----------------------------------------')
    try:
        convert_bioentity.convert(old_session_maker, new_session_maker, ask=False)  
    except Exception:
        write_to_output_file( "Unexpected error:", sys.exc_info()[0])
        
    write_to_output_file( '----------------------------------------')
    write_to_output_file( 'Convert References')
    write_to_output_file( '----------------------------------------')
    try:
        convert_reference.convert(old_session_maker, new_session_maker, ask=False)
    except Exception:
        write_to_output_file( "Unexpected error:", sys.exc_info()[0])
      
    write_to_output_file( '----------------------------------------')
    write_to_output_file( 'Convert Evelements')
    write_to_output_file( '----------------------------------------'  )
    try:
        convert_evelements.convert(old_session_maker, new_session_maker, ask=False)
    except Exception:
        write_to_output_file( "Unexpected error:", sys.exc_info()[0])
        
    send_output_email()
        