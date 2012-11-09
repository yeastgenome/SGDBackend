'''
Created on Nov 8, 2012

@author: kpaskov
'''

class ParseParameters():

    def __init__(self, parameter):

        unique_name = []
        found_name = {}
        task_list = []
        
        task_dict = eval(parameter)
        
        for task in sorted(task_dict.keys()):

            (genes, comment) = task_dict[task]
            
            names = []

            if genes:
                gene_list = genes.split()
                for name in gene_list:
                    names.append(name)
                    if not found_name.has_key(name):
                        found_name[name] = 1
                        unique_name.append(name)
                        
            task_list.append([task, names, comment])

        self.tasks = task_list
        self.genes = unique_name

    def get_tasks(self):
        return self.tasks

    def get_genes(self):
        return self.genes
    
    # medline_journal

## need to find out if there is a web service we can call to get the journal full name
## and ISSN/ESSN for a journal abbreviation 
medlineFile = 'J_Medline.txt'  # or need to put this file into a public place

class MedlineJournal():

    def __init__(self, abbrev):
        lines = [line.strip() for line in open(medlineFile)]
    
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
                    

        
    