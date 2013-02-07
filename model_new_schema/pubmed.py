from Bio import Entrez, Medline
import os


def get_medline_data(pubmed_id):
    """
    Grab information on this pubmed_id from ncbi using FetchMedline()
    """
    medline = FetchMedline(pubmed_id)
    records = medline.get_records()
    for rec in records:
        record = rec
    return Pubmed(record)
    
class FetchMedline():

    def __init__(self, pmid):
        Entrez.email = 'sgd-programmers@genome.stanford.edu'
        ## pmids is a list (array of pmid)
        handle = Entrez.efetch(db='pubmed', id=pmid, rettype='medline', retmode='text')
        self.records = Medline.parse(handle)

    def get_records(self):
        return self.records
    
# medline_journal
## need to find out if there is a web service we can call to get the journal full name
## and ISSN/ESSN for a journal abbreviation 

this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, 'J_Medline.txt')

class MedlineJournal():

    def __init__(self, abbrev):
        lines = [line.strip() for line in open(DATA_PATH)]
    
        self.journal_title = ''
        self.issn = ''
        self.essn = ''
        med_abbr = ''

        for line in lines:

            if '-------' in line:
                continue

            record = line.split(':')

            if record[0] == 'NlmId' and med_abbr == abbrev:
                break

            if record[0] == 'JournalTitle':

                self.journal_title = record[1].strip()

                if record[0] == 'ISSN':
                    self.issn = record[1].strip()
                else:
                    self.issn = ''

                if record[0] == 'ESSN':
                    self.essn = record[1].strip()
                else:
                    self.essn = ''
                    
                if record[0] == 'MedAbbr':
                    self.med_abbr = record[1].strip()


class Pubmed():

    def __get_entry(self, key):
        if self.record.has_key(key):
            return self.record[key]
        return ''
    
    def __get_pub_type(self):
        if self.record.has_key('PT'):
            pubtype = self.record['PT'][0]
            if (pubtype == 'JOURNAL ARTICLE'):
                pubtype = 'Journal Article'  ## need a conf for the mapping
            return pubtype
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
        

    
