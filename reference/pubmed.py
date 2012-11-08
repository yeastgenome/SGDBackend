from Bio import Entrez
from Bio import Medline

class FetchMedline():

    def __init__(self, pmids):
        
         Entrez.email = 'sgd-programmers@genome.stanford.edu'

         ## pmids is a list (array of pmid)
         handle = Entrez.efetch(db='pubmed', id=pmids, rettype='medline', retmode='text')
         self.records = Medline.parse(handle)

    def get_records(self):
        return self.records


class Pubmed():

    def __get_entry(self, key):
        if self.record.has_key(key):
            return self.record[key]
        return ''
    
    def __get_pub_type(self):
        if self.record.has_key('PT'):
            type = self.record['PT'][0]
            if (type == 'JOURNAL ARTICLE'):
                type = 'Journal Article'  ## need a conf for the mapping
            return type
        return ''

    def __get_publish_status(self):
        if self.record.has_key('PST'):
            if self.record['PST'].find('aheadofprint'):
                return 'Epub ahead of print'
        return 'Published'

    def __get_pdf_status(self):
        if self.record.has_key('PST'):
            if self.record['PST'].find('aheadofprint'):
                return 'NAP'
        return 'N'

    def __get_citation(self):

        author = self.__get_entry('AU')
        num_of_author = len(author)

        if num_of_author == 0:
            return ''

        citation = ''

        if num_of_author >= 3:
            citation = author[0] + ', et al.'
        elif num_of_author == 2:
            citation = author[0] +  ' and ' + author[1]
        else:
            citation = author[0]
            
        citation += ' (' + self.__get_year('DP') + ') '
        citation += self.__get_entry('TI')     
        citation += ' ' + self.__get_entry('TA') 
        citation += ' ' + self.__get_entry('VI')
        citation += '(' + self.__get_entry('IP') + ')'
        page = self.__get_entry('PG')
        if page:
            citation += ':' + self.__get_entry('PG')
        citation.strip()
        return citation

        
    def __get_year(self, key):
        if self.record.has_key(key):
            date = self.record[key].split(' ') 
            return date[0]
        return ''


    def __init__(self, record):
        self.record = record
        self.abstract_txt = self.__get_entry('AB')
        self.title = self.__get_entry('TI')
        self.authors = self.__get_entry('AU')
        self.date_published = self.__get_entry('DP')
        self.entry_date = self.__get_entry('DA')
        self.year = self.__get_year('DP')
        self.journal_abbrev = self.__get_entry('TA')
        self.volume = self.__get_entry('VI')
        self.pages = self.__get_entry('PG')
        self.issue = self.__get_entry('IP')
        self.last_revised = self.__get_entry('LR')
        self.pub_type = self.__get_pub_type()
        self.publish_status = self.__get_publish_status()
        self.pdf_status = self.__get_pdf_status()
        self.citation = self.__get_citation()
        

    
