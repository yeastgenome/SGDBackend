# medline_journal

## need to find out if there is a web service we can call to get the journal full name
## and ISSN/ESSN for a journal abbreviation 
medlineFile = '/home/shuai/J_Medline.txt'  # or need to put this file into a public place

class MedlineJournal():

    def __init__(self, abbrev):
        
        lines = [line.strip() for line in open(medlineFile)]
    
        journal_title = ''
        issn = ''
        essn = ''
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
        
    
                    
