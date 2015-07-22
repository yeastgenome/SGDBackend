from src.sgd.convert import basic_convert
from src.sgd.convert.util import is_number

__author__ = 'sweng66'

def source_starter(bud_session_maker):

    from src.sgd.model.bud.cv import Code
    bud_session = bud_session_maker()

    id2dateCreated = {}
    id2createdBy = {}
    for bud_obj in bud_session.query(Code).all():
        id2dateCreated[bud_obj.id] = bud_obj.date_created
        id2createdBy[bud_obj.id] = bud_obj.created_by

    file_names = ['src/sgd/convert/data/source_data_toload.txt']
    
    for file_name in file_names:
        print file_name
        f = open(file_name, 'rU')
        header = True
        for line in f:
            if header:
                header = False
            else:
                items = line.split('\t')
                source = items[0]
                bud_id = items[1]

                print source

                desc = items[2].replace('"', '')     
                obj_json = {'display_name': source }
                if is_number(bud_id):
                    id = int(bud_id)
                    obj_json['bud_id'] = id
                    if id2dateCreated.get(id):
                        obj_json['date_created'] = str(id2dateCreated.get(id))
                    if id2createdBy.get(int(bud_id)):
                        obj_json['created_by'] = id2createdBy.get(id)
                if desc:
                    obj_json['description'] = desc
                
                yield obj_json
                    
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, source_starter, 'source', lambda x: x['display_name'])



