'''
Created on Feb 27, 2013

@author: kpaskov
'''
from sgd2.models import DBSession
from sqlalchemy.sql.expression import func
import string

def add_gene_hyperlinks(text):
    text = str(text) 
    if text is None:
        return None
    search_text = text.upper().translate(string.maketrans("",""), string.punctuation).split()
    result = validate_genes(search_text)
    bioentities = result['bioentities']
    word_to_link = {}
    for name, bioent in bioentities.iteritems():
        word_to_link[name.upper()] = bioent.link
        
    words = text.split()
    for i in range(0, len(words)):
        upper = words[i].upper()
        if upper in word_to_link:
            word = words[i]
            words[i] = "<a href='" + word_to_link[upper] + "'>" + word + "</a>"
        else:
            remove_punc = upper.translate(string.maketrans("",""), string.punctuation)
            if remove_punc in word_to_link:
                link = word_to_link[remove_punc]
                index = words[i].upper().find(remove_punc)
                if index >= 0:
                    word = words[i]
                    words[i] = word[:index] + "<a href='" + link + "'>" + word[index:index+len(remove_punc)] + "</a>" + word[index+len(remove_punc):]
            
    return ' '.join([x for x in words])
    
def validate_genes(gene_names, session=None):
    """
    Convert a list of gene_names to a mapping between those gene_names and features.
    """            
    from model_new_schema.bioentity import Bioentity
    
    if gene_names is not None and len(gene_names) > 0:
        upper_gene_names = [x.upper() for x in gene_names]
        fs_by_name = set(DBSession.query(Bioentity).filter(func.upper(Bioentity.name).in_(upper_gene_names)).filter(Bioentity.bioent_type != 'CHROMOSOME').all())
        fs_by_gene_name = set(DBSession.query(Bioentity).filter(func.upper(Bioentity.secondary_name).in_(upper_gene_names)).filter(Bioentity.bioent_type != 'CHROMOSOME').all())
            
        all_names_left = set(upper_gene_names)
      
        #Create table mapping name -> Feature        
        name_to_feature = {}
        for f in fs_by_name:
            name_to_feature[f.name.upper()] = f
        for f in fs_by_gene_name:
            name_to_feature[f.secondary_name.upper()] = f
    
        all_names_left.difference_update(name_to_feature.keys())
              
        return {'bioentities':name_to_feature, 'not_genes':all_names_left}
    else:
        return {'bioentities':{}, 'not_genes':set()} 