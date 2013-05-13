'''
Created on Apr 24, 2013

@author: kpaskov
'''

gene_keys = [
            {'field_name':'alias_str', 'word_type':'ALIAS', 'use_for_typeahead':'Y', 'use_for_search':'Y', 'divide_into_words':'Y'},
            {'field_name':'official_name', 'word_type':'NAME', 'use_for_typeahead':'Y', 'use_for_search':'Y', 'divide_into_words':'N'},
            {'field_name':'secondary_name', 'word_type':'GENE_NAME', 'use_for_typeahead':'Y', 'use_for_search':'Y', 'divide_into_words':'N'},
            
            ]

biocon_keys = [
            {'field_name':'name', 'word_type':'NAME', 'use_for_typeahead':'Y', 'use_for_search':'Y', 'divide_into_words':'Y'},
            ]

reference_keys = [
            {'field_name':'year', 'word_type':'PUBMED_ID', 'use_for_typeahead':'Y', 'use_for_search':'Y', 'divide_into_words':'whole'},
            {'field_name':'pubmed_id', 'word_type':'PUBMED_ID', 'use_for_typeahead':'Y', 'use_for_search':'Y', 'divide_into_words':'whole'},
            #{'field_name':'title', 'word_type':'TITLE', 'use_for_typeahead':'Y', 'use_for_search':'Y', 'divide_into_words':'Y'},
            {'field_name':'author_year', 'word_type':'AUTHOR_YEAR', 'use_for_typeahead':'Y', 'use_for_search':'Y', 'divide_into_words':'N'},
            ]

def add_bioents_to_typeahead(new_session):
    from model_new_schema.bioentity import Bioentity, Gene
    from model_new_schema.bioconcept import Bioconcept
    from model_new_schema.reference import Reference


#        
#    genes = new_session.query(Gene).all()
#    i = 0
#    total = len(genes)
#    for gene in genes:
#        add_obj_to_typeahead(new_session, gene, gene_keys)
#        i = i+1
#        if i%1000 == 0:
#            new_session.commit()
#            print str(i) + '/' + str(total)
#            
#        
#    biocons = new_session.query(Bioconcept).all()
#    i = 0
#    total = len(biocons)
#    for biocon in biocons:
#        add_obj_to_typeahead(new_session, biocon, biocon_keys)
#        i = i+1
#        if i%1000 == 0:
#            new_session.commit()
#            print str(i) + '/' + str(total)
        
    references = new_session.query(Reference).all()
    i = 0
    total = len(references)
    for reference in references:
        add_obj_to_typeahead(new_session, reference, reference_keys)
        i = i+1
        if i%1000 == 0:
            new_session.commit()
            print str(i) + '/' + str(total)
    

def add_obj_to_typeahead(new_session, obj, keys):
    from model_new_schema.search import Typeahead
    
    word_to_type = {}
    for key in keys:
        value = getattr(obj, key['field_name'])
        if value != None:
            if key['divide_into_words'] == 'Y':
                dashes_replaced = value.replace('-', ' ')
                for ind_value in dashes_replaced.split():
                    words = generate_words(ind_value)
                    word_to_type.update([(word, key['word_type']) for word in words])
            elif key['divide_into_words'] == 'N':
                words = generate_words(value)
                word_to_type.update([(word, key['word_type']) for word in words])
            else:
                word_to_type[value] = key['word_type']
                
    for word, word_type in word_to_type.iteritems():
        typeahead_entry = Typeahead(word, obj.type, obj.id, word_type)
        new_session.add(typeahead_entry)

def generate_words(word):
    words = set()
    clean_word = str(word).rstrip('?:!.,;').lower()
    for i in range (0, len(clean_word)):
        words.add(clean_word[:i+1])
    return words
    


            
            
            
            