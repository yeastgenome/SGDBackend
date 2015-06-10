import urllib
import shutil
import gzip
import datetime

def download_file(baseURL, filename):

    urllib.urlretrieve(baseURL + filename, filename)
    
    ## unzip file and move it to data directory
    ## actually we can simply update the loading script to read the data in directly from gp file
    ## gzip.read(filename). Well for now, just unzip it this way - little silly but we have a local
    ## copy of the unzipped file 
    unzippedFileName = "./data/" + filename[:-3]
    with gzip.open(filename, 'rb') as infile:
        with open(unzippedFileName, 'w') as outfile:
            for line in infile:
                outfile.write(line)

    ## archive file with a date stamp                                                                                
    today = datetime.datetime.now().date()
    archiveFileName = "./data/" + filename[:-3] + "_" + str(today) + ".gz"
    shutil.move(filename, archiveFileName)
    

if __name__ == "__main__":

    baseURL = 'ftp://ftp.ebi.ac.uk/pub/contrib/goa/'
    gpad_file = 'gp_association.559292_sgd.gz'
    gpi_file = 'gp_information.559292_sgd.gz'

    download_file(baseURL, gpad_file)
    download_file(baseURL, gpi_file)
