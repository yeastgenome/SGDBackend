from Bio import Entrez, Medline
        
class FetchMedline():

    def __init__(self, pmid):
        Entrez.email = 'sgd-programmers@genome.stanford.edu'
        handle = Entrez.efetch(db='pubmed', id=pmid, rettype='medline', retmode='text')
        self.records = Medline.parse(handle)

    def get_records(self):
        return self.records
                    
