from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def phenotype_starter(bud_session_maker):
    from src.sgd.model.bud.phenotype import Phenotype
    from src.sgd.model.nex.apo import Apo

    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    observable_to_id = {}
    qualifier_to_id = {}
    for nex_obj in nex_session.query(Apo).all():
        if nex_obj.apo_namespace == 'observable':
            observable_to_id[nex_obj.display_name] = nex_obj.id
        if nex_obj.apo_namespace == 'qualifier':
            qualifier_to_id[nex_obj.display_name] = nex_obj.id
            
    for bud_obj in bud_session.query(Phenotype).all():
        observable_id = observable_to_id.get(bud_obj.observable)
        if observable_id is None:
            print "The observable =", bud_obj.observable, " is not found in APO table." 
            continue
        obj_json = {
            'source': {'display_name': 'SGD'},
            'observable': bud_obj.observable,
            'observable_id': observable_id,    
            'bud_id': bud_obj.id,
            'date_created': str(bud_obj.date_created),
            'created_by': bud_obj.created_by
            }
        if bud_obj.qualifier is not None and qualifier_to_id.get(bud_obj.qualifier) is not None:
            obj_json['qualifier'] = bud_obj.qualifier
            obj_json['qualifier_id'] = qualifier_to_id.get(bud_obj.qualifier)

        yield obj_json

    bud_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, phenotype_starter, 'phenotype', lambda x: (x['observable'], x.get('qualifier')))


