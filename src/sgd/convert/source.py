from src.sgd.convert import basic_convert
from src.sgd.convert.util import is_number

__author__ = 'sweng66'

def source_starter(bud_session_maker):

    from src.sgd.model.bud.cv import Code
    bud_session = bud_session_maker()

    id2dateCreated = {}
    # id2createdBy = {}
    for bud_obj in bud_session.query(Code).all():
        id2dateCreated[bud_obj.id] = bud_obj.date_created
        # id2createdBy[bud_obj.id] = bud_obj.created_by

    file_names = ['src/sgd/convert/data/SOURCE-cleanup_20160929.txt']

    source_old_to_new = source_mapping()

    for file_name in file_names:
        print file_name
        f = open(file_name, 'rU')
        header = True
        for line in f:
            if header:
                header = False
            else:
                items = line.split('\t')
                if len(items) < 7:
                    continue
                format_name = items[1]
                display_name = items[2]
                if display_name in source_old_to_new:
                    display_name = source_old_to_new[display_name]
                    format_name = display_name.replace(" ", "_")
                bud_id = items[3]
                if bud_id == '(null)':
                    bud_id = ''
                desc = items[4].replace('"', '')
                date_created = items[5]
                created_by = items[6]
                obj_json = {'format_name': format_name,
                            'display_name': display_name,
                            'created_by': created_by}
                if is_number(bud_id):
                    id = int(bud_id)
                    obj_json['bud_id'] = id
                    if id2dateCreated.get(id):
                        obj_json['date_created'] = str(id2dateCreated.get(id))
                if desc:
                    obj_json['description'] = desc
                
                yield obj_json


def source_mapping():

    return { "Direct Submission": "Direct submission",
             "Hamap": "HAMAP",
             "LoQate": "LoQAte",
             "PhosphoPep Database": "PhosphoPep",
             "ProSitePatterns": "PROSITE",
             "ProSiteProfiles": "PROSITE",
             "SignalP_EUK": "SignalP",
             "SignalP_GRAM_POSITIVE": "SignalP",
             "Uniprot": "UniProt" }

                    
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, source_starter, 'source', lambda x: x['display_name'])



