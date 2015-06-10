import filecmp
import os.path
import urllib
# import shutil
from src.sgd.convert.into_curate.interaction_config import email_receiver, email_subject
from src.sgd.convert.into_curate.util import sendmail
from src.sgd.convert.into_curate.physinteractionannotation import convert as physconvert
from src.sgd.convert.into_curate.geninteractionannotation import convert as genconvert

def update_interaction(biogrid_file):
    
    ## physconvert(biogrid_file)
    physconvert('pastry.stanford.edu:1521', 'curator-dev-db')
    ## genconvert('pastry.stanford.edu:1521', 'curator-dev-db')
    
if __name__ == "__main__":
    
    url_path = "http://www.thebiogrid.org/downloads/datasets/"
    biogrid_file = "SGD.tab.txt"
    old_biogrid_file = "/tmp/SGD.tab.txt"
    urllib.urlretrieve(url_path + biogrid_file, biogrid_file)
    if os.path.isfile(old_biogrid_file):
        if filecmp.cmp(biogrid_file, old_biogrid_file):
            print "BioGrid is not updated last week!"
            message = "BioGrid is not updated last week!"
            sendmail(email_subject, message, email_receiver)
            exit    

    update_interaction(biogrid_file)

    # shutil.move(biogrid_file, old_biogrid_file)
