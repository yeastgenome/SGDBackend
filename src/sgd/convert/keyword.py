from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'


def keyword_starter(bud_session_maker):
    
    f = open('src/sgd/convert/data/category2keywordDefMapping.txt', 'r')
    category_to_def_mapping = {}
    for line in f:
        row = line.split('\t')
        category_to_def_mapping[row[0]] = row[1].strip()
    f.close()

    f = open('src/sgd/convert/data/category2keywordMapping.txt', 'r')
    category_to_keyword_mapping = {}
    for line in f:
        row = line.split('\t')
        if len(row) >= 2:
            category_to_keyword_mapping[row[1].strip()] = row[0]
        yield remove_nones({
                'display_name': row[0],
                'description': category_to_def_mapping.get(row[0]),
                'source': {'display_name': 'SGD'}
        })

    f.close()

    ### spell tags

    keywords = {}
    f = open('src/sgd/convert/data/microarray_05_14/pmid_filename_gse_conds_tags_file_20150416_forNex.txt', 'r')
    for line in f:
        row = line.split('\t')
        tag = row[6].strip()
        for t in [x.strip() for x in tag.split('|')]:
            if t in ['Other', 'other']:
                continue
            
            display_name = t
            if category_to_keyword_mapping.get(t):
                display_name = category_to_keyword_mapping.get(t)
                
            if display_name in keywords:
                continue
            keywords[display_name] = 1

            yield remove_nones({
                'display_name': display_name,
                'description': category_to_def_mapping.get(t),
                'source': {'display_name': 'SGD'}
            })
    f.close()

    from src.sgd.model.bud.colleague import Keyword
    bud_session = bud_session_maker()
    for bud_obj in bud_session.query(Keyword).filter_by(source='Curator-defined').all():
        if bud_obj.keyword in ['Other', 'other']:
            continue
        keyword = ''
        if bud_obj.keyword.startswith('RNA') or bud_obj.keyword.startswith('DNA'):
            keyword = bud_obj.keyword
        else:
            keyword = bud_obj.keyword.lower()
        display_name = keyword 
        if category_to_keyword_mapping.get(keyword):
            display_name = category_to_keyword_mapping[keyword]

        if display_name in keywords:
            continue
        keywords[display_name] = 1

        yield {'display_name': display_name,
               'source': {'display_name': 'SGD'},
               'bud_id': bud_obj.id,
               'date_created': str(bud_obj.date_created),
               'created_by': bud_obj.created_by}
    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, keyword_starter, 'keyword', lambda x: x['display_name'])


