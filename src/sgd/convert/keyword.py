from src.sgd.convert import basic_convert

__author__ = 'sweng66'


def keyword_starter(bud_session_maker):
    
    f = open('src/sgd/convert/data/keyword.txt', 'r')
    for line in f:
        row = line.strip().split('\t')
        desc = row[3]
        if desc is None or desc == 'None':
            desc = ''
        yield { 'format_name': row[0],
                'display_name': row[1],
                'link': row[2],
                'description': desc,
                'source': {'display_name': 'SGD'},
                'date_created': row[4],
                'created_by': row[5]}

    f.close()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, keyword_starter, 'keyword', lambda x: x['display_name'])


