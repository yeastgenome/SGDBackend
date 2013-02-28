'''
Created on Feb 27, 2013

@author: kpaskov
'''
from jsonify.mini import bioent_mini
from sgd2.models import DBSession
from sqlalchemy.sql.expression import func
import string

def add_gene_hyperlinks(text):
    search_text = text.upper().translate(string.maketrans("",""), string.punctuation).split()
    result = validate_genes(search_text)
    bioentities = result['bioentities']
    word_to_link = {}
    for name, bioent in bioentities.iteritems():
        bioent_json = bioent_mini(bioent)
        word_to_link[name.upper()] = bioent_json['link']
        
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
    
    from model_new_schema.bioentity import Bioentity, Alias

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
    
        print name_to_feature
        all_names_left.difference_update(name_to_feature.keys())
            
        #if len(all_names_left) > 0:
        #    aliases = session.query(Alias).filter(func.upper(Alias.name).in_(all_names_left)).all()
        #else:
        #    aliases = []

        #Create table mapping name -> Alias
        name_to_alias = {}
        #for a in aliases:
        #    features = [f for f in a.features if f.type != 'chromosome']
        #    if len(features) > 0:
        #        if a.name in name_to_alias:
        #            name_to_alias[a.name.upper()].update(features)
        #        else:
        #            name_to_alias[a.name.upper()] = set(features)
                        
        #This may be a gene name with p appended
        #p_endings = [word[:-1] for word in all_names_left if word.endswith('P')]
        #p_ending_fs_by_name = set(session.query(Feature).filter(func.upper(Feature.name).in_(p_endings)).filter(Feature.type != 'chromosome').all())
        #p_ending_fs_by_gene_name = set(session.query(Feature).filter(func.upper(Feature.gene_name).in_(p_endings)).filter(Feature.type != 'chromosome').all())
            
        #all_names_left.difference_update(name_to_alias.keys())
             
        #Add to Alias table all p-ending gene names
        #for p_ending in p_ending_fs_by_name:
        #    word = p_ending.name + 'P'
        #    if word in name_to_alias:
        #        name_to_alias[word.upper()].add(p_ending)
        #    else:
        #        name_to_alias[word.upper()] = set([p_ending])
                    
        #for p_ending in p_ending_fs_by_gene_name:
        #    word = p_ending.gene_name + 'P'
        #    if word in name_to_alias:
        #        name_to_alias[word.upper()].add(p_ending)
        #    else:
        #        name_to_alias[word.upper()] = set([p_ending])
                               
               
        return {'bioentities':name_to_feature, 'aliases':name_to_alias, 'not_genes':all_names_left}
    else:
        return {'bioentities':{}, 'aliases':{}, 'not_genes':set()}
        