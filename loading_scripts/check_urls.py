'''
Created on Jun 7, 2013

@author: kpaskov
'''
from eventlet.green import urllib2
from model_new_schema import config as new_config
from random import shuffle
from schema_conversion import prepare_schema_connection
from urllib2 import HTTPError
import datetime
import eventlet
import httplib
import model_new_schema
    
class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"
        
#http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists
def url_response(url_info): 
    url_id = url_info[0]
    url = url_info[1]  
    redirect_url = None
    code = None
    try:
        response = urllib2.urlopen(url, timeout=1)
        real_url = response.geturl()
        code = str(response.getcode())
        if real_url != url:
            redirect_url = real_url
    except Exception as e:
        if hasattr(e, 'code'):
            code = str(e.code)
        else:
            code = str(e)
        
    return (url_id, url, code, redirect_url)
    


def check(session_maker):
    #The following imports are needed due to Url being polymorphic
    from model_new_schema.misc import Url
    from model_new_schema.reference import ReferenceUrl
    from model_new_schema.bioentity import BioentUrl
    # Check Urls
    print 'Url'
    start_time = datetime.datetime.now()
    try:
        session = session_maker()
        urls = session.query(Url).all()
        urls = [(url.id, url.url) for url in urls]
        print 'URLs loaded.'

        bad_url_f = open('/Users/kpaskov/Documents/bad_urls.txt', 'w')
        redirect_url_f = open('/Users/kpaskov/Documents/redirect_urls.txt', 'w')
        all_responses = {}
        pool = eventlet.GreenPool()
        for response in pool.imap(url_response, urls):
            url_id = response[0]
            url = response[1]
            code = response[2]
            redirect_url = response[3]
            
            if code in all_responses:
                all_responses[code] = all_responses[code] + 1
            else:
                all_responses[code] = 1
                
            if code not in ('200', '301', '302'):
                bad_url_f.write(str(url_id) + '\t' + url + '\t' + code + '\n')
                
            if redirect_url is not None:
                redirect_url_f.write(str(url_id) + '\t' + url + '\t' + redirect_url + '\n')

        bad_url_f.close()  
        redirect_url_f.close()
        print all_responses
    finally:
        session.close()
    
    print datetime.datetime.now() - start_time

if __name__ == "__main__":
    session_maker = prepare_schema_connection(model_new_schema, new_config)
    #check(session_maker)
    print url_response((1, 'http://www.karger.com?DOI=10.1007/s11373-005-9027-9'))
    
    
