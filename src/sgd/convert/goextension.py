from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id, read_gpi_file, \
    read_gpad_file, get_go_extension_link

__author__ = 'sweng66'

GPI_FILE = 'src/sgd/convert/data/gp_information.559292_sgd'
GPAD_FILE = 'src/sgd/convert/data/gp_association.559292_sgd'

def goextension_starter(bud_session_maker):

    from src.sgd.model.nex.goannotation import Goannotation

    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    key_to_annotation_id = {}
    for x in nex_session.query(Goannotation).all():
        key = (x.dbentity_id, x.go_id, x.eco_id, x.reference_id, x.annotation_type, x.source.display_name, x.go_qualifier)
        key_to_annotation_id[key] = x.id

    ## load the annotations with source = 'SGD' and the annotations with go_evidence = 'IEA' from GPAD file

    [uniprot_to_date_assigned, uniprot_to_sgdid_list] = read_gpi_file(GPI_FILE)

    get_extension = 1
    data = read_gpad_file(GPAD_FILE, nex_session, uniprot_to_date_assigned, 
                          uniprot_to_sgdid_list, get_extension)

    for x in data:

        key = (x['dbentity_id'], x['go_id'], x['eco_id'], x['reference_id'], x['annotation_type'], x['source'], x['go_qualifier'])
        annotation_id = key_to_annotation_id.get(key)

        if annotation_id is None:
            print "The goannotatuon key: ", key, " is not in GOANNOTATION table."
            continue

        groups = x['goextension'].split('|')
        group_id = 0
        for group in groups:
            members = group.split(',')
            group_id = group_id + 1
            for member in members:
                print "member=", member
                pieces = member.split('(')
                role = pieces[0].replace('_', ' ')
                ro_id = get_relation_to_ro_id(role)
                if ro_id is None:
                    print role, " is not in RO table."
                    continue
                dbxref_id = pieces[1][:-1]
                link = get_go_extension_link(dbxref_id)
                if link.startswith('Unknown'):
                    print "unknown ID: ", dbxref_id
                    continue

                yield { 'annotation_id': annotation_id,
                        'group_id': group_id,
                        'ro_id': ro_id,
                        'dbxref_id': dbxref_id,
                        'link': link }


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()
   
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, goextension_starter, 'goextension', lambda x: (x['annotation_id'], x['group_id'], x['dbxref_id'], x['link'], x['ro_id']))


