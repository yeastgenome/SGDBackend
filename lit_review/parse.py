'''
Created on Nov 8, 2012

@author: kpaskov
'''

class ParseParameters():

    def __init__(self, parameter):

        self.all_gene_names = set()
        self.tasks = []
        
        task_dict = eval(parameter)
        
        for task in sorted(task_dict.keys()):
            (genes, comment) = task_dict[task]

            gene_names = []
            if genes:
                gene_names = genes.split()
                self.all_gene_names.update(gene_names)
                
            task_type = {'High Priority': TaskType.HIGH_PRIORITY,
                         'Delay': TaskType.DELAY,
                         'HTP phenotype': TaskType.HTP_PHENOTYPE_DATA,
                         'Non-phenotype HTP': TaskType.OTHER_HTP_DATA,
                         'GO information': TaskType.GO_INFORMATION,
                         'Classical phenotype information': TaskType.CLASSICAL_PHENOTYPE_INFORMATION,
                         'Headline information': TaskType.HEADLINE_INFORMATION,
                         'Reviews': TaskType.REVIEWS,
                         'Add to database': TaskType.ADD_TO_DATABASE
            }[task]
             
            
                        
            self.tasks.append(Task(task_type, gene_names, comment))

    def get_tasks(self):
        return self.tasks

    def get_all_gene_names(self):
        return self.all_gene_names

class Task():
    def __init__(self, task_type, gene_names, comment):
        if task_type == TaskType.ADD_TO_DATABASE: self.name = 'Gene Link'; self.topic = 'Additional Literature'
        elif task_type == TaskType.REVIEWS: self.name = 'Gene Link'; self.topic = 'Reviews'
        elif task_type == TaskType.HTP_PHENOTYPE_DATA: self.name = 'HTP phenotype'; self.topic = 'Omics'
        elif task_type == TaskType.CLASSICAL_PHENOTYPE_INFORMATION: self.name = 'Classical phenotype information'; self.topic = 'Primary Literature'
        elif task_type == TaskType.DELAY: self.name = 'Delay'; self.topic = 'Primary Literature'
        elif task_type == TaskType.GO_INFORMATION: self.name = 'GO information'; self.topic = 'Primary Literature'
        elif task_type == TaskType.HEADLINE_INFORMATION: self.name = 'Headline information'; self.topic = 'Primary Literature'
        elif task_type == TaskType.HIGH_PRIORITY: self.name = 'High Priority'; self.topic = 'Primary Literature'
        elif task_type == TaskType.OTHER_HTP_DATA: self.name = 'Non-phenotype HTP'; self.topic = 'Primary Literature'
        
        self.type = task_type
        self.gene_names = gene_names
        self.comment = comment
        
class TaskType:
    HIGH_PRIORITY=0
    DELAY=1
    HTP_PHENOTYPE_DATA=2
    OTHER_HTP_DATA=3
    GO_INFORMATION=4
    CLASSICAL_PHENOTYPE_INFORMATION=5
    HEADLINE_INFORMATION=6
    REVIEWS=7
    ADD_TO_DATABASE=8
    

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
                    

        
    