from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def dosubset_starter(bud_session_maker):
    
    from src.sgd.model.nex.do import Do
    
    nex_session = get_nex_session()

    do_name_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Do).all()])

    ## https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/doid.obo
    f = open('src/sgd/convert/data/doid.obo')
    name = None
    doid = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            name = None
            doid = None
        if line.startswith('id: '):
            doid = line[4:]
        if line.startswith('name: '):
            name = line[6:]
        if line.startswith('subset: '):
            subset_name = line[8:]
            if len(subset_name) > 45:
                print "The subset_name is too long: ", subset_name, len(subset_name)
                continue

            if name and doid:
                do_id = do_name_to_id.get(name)
                if do_id is not None:
                    yield { "display_name": name,
                            "format_name": subset_name + "_" + doid,
                            "do_id": do_id,
                            "link": "/dosubset/" + doid,
                            "source": { "display_name": "DO" },
                            "subset_name": subset_name,
                            "genome_count": 0 }

    f.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()
        
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dosubset_starter, 'dosubset', lambda x: (x['display_name'], x['format_name'], x['do_id'], x['subset_name'], x['genome_count']))



