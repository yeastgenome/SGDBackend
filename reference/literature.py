"""
Name: literature.py

This module contains routines used to retrieve the reference/lit_guide related
data from oracle database and to update the data in the database..

Shuai Weng, 7/2012

"""

from models import db
from models import Feature
from models import Reference 
from models import RefTemp
from models import RefCuration
from models import LitGuide
from models import LitGuideFeat


## we need to move this class to some where else so other applications can access it if needed

class ValidateGenes():

    def __init__(self, genes):

        bad_name = []
        good_name = {}
        
        for name in genes:
            if name:
                featRow = Feature.search(name)
                if featRow == None:
                    bad_name.append(name)
                else:
                    good_name[name] = featRow.feature_no
        self.bad_entry = bad_name            
        self.good_entry = good_name
            
    def invalid_names(self):
        return self.bad_entry

    def name_to_primary_key(self):
        return self.good_entry

    
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
    

class ReferenceLink():

    def __init__(self, pmid, user, parameters):
        
        parameter = ParseParameters(parameters)

        genes = parameter.get_genes()

        validation = ValidateGenes(genes)

        self.invalid_genes = validation.invalid_names()

        self.user = user
        
        if len(self.invalid_genes) == 0:
            
            self.tasks = parameter.get_tasks()

            self.feature_no_for_name = validation.name_to_primary_key()

            self.pmid = pmid

    def invalid_names(self):
        return self.invalid_genes

    
    def insert_and_associate(self):
    
        ref_no = Reference.insert(self.pmid, self.user)
        RefTemp.delete(self.pmid)
        
        lg_feat_hash = {}
        message = ''
        topic_added = {}
        task_added = {}

        if len(self.tasks) == 0:
            return None

        for task_entry in self.tasks:
        
            task = task_entry[0]    
            genes = task_entry[1]
            comment = task_entry[2]
            
            if len(genes) > 0:

                feat_no_list = []
            
                topic1 = ''
                topic2 = ''
                if 'Add to' in task:
                    topic1 = 'Non-focused set'
                elif 'Review' in task:
                    topic1 = task
                    topic2 = 'Focused set'
                else:
                    topic1 = 'Focused set'
            
                if 'Review' in task or 'Add to' in task:
                    task = 'Gene Link'

                message += "Curation_task = '" + task
                message += "', literature_topic = '" + topic1 + "'"
                
                if topic2:
                    message += " and '" + topic2 + "'"
                message += ", gene = "
                 
                for name in genes:
                    feat_no = self.feature_no_for_name[name]
                    feat_no_list.append(feat_no)
                    ## insert into ref_curation
                    if not task_added.has_key((feat_no, task)):
                        RefCuration.insert(ref_no, task, self.user, feat_no, comment)            
                        task_added[(feat_no, task)] = 1
                    message += name + '|'

                if comment:
                    message += ", comment = '" + comment + "'"
                    
                message += "<br>"
            
                ## insert into lit_guide + litguide_feat
                for topic in [topic1, topic2]:
                    if topic == '':
                        continue
                    if topic_added.has_key(topic):
                        litguide_no = topic_added[topic]
                    else:
                        litguide_no = LitGuide.insert(ref_no, topic, self.user)
                        topic_added[topic] = litguide_no
            
                    for feat_no in feat_no_list:
                        key = (feat_no, litguide_no)
                        if lg_feat_hash.has_key(key):
                            continue
                        lg_feat_hash[key] = 1
                        LitGuideFeat.insert(feat_no, litguide_no)
                    
            else:   ## no gene name provided

                ## if no gene name provided and "Add to database" was checked,
                ## no need to add any association
                if 'Add' in task:
                    continue

                ## if it is a review, no need to add to ref_curation
                if 'Review' in task:
                    ## topic = task = 'Reviews'
                    LitGuide.insert(ref_no, task, self.user)
                    message += "Literature_topic = '" + task + "'<br>"
                    continue

                if not task_added.has_key((0, task)):
                    RefCuration.insert(ref_no, task, self.user, None, comment)
                    task_added[(0, task)] = 1
                
                    message += "Curation_task = '" + task + "'"
            
                ## insert into lit_guide 
                if 'HTP' in task or 'Review' in task:

                    topic = ''
                    if 'HTP' in task:
                        topic = 'Omics'
                    else:
                        # 'Review' in task:
                        topic = task
                    
                    if topic_added.has_key(topic):
                        if comment:
                            message += ", comment = '" + comment + "'"
                        message += "<br>"
                        continue
                    else:    
                        lit_guide_no = LitGuide.insert(ref_no, topic, self.user)
                        topic_added[topic] = lit_guide_no 
                        message += ", literature_topic = '" + topic

                if comment:
                    message += ", comment = '" + comment + "'"
                    
                message += "<br>"
                
            db.session.commit()

        return message

        
