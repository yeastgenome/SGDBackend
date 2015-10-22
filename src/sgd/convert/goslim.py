from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def goslim_starter(bud_session_maker):

    from src.sgd.model.nex.go import Go
    from src.sgd.model.bud.go import GoSet 
    
    bud_session = bud_session_maker()
    nex_session = get_nex_session()
    
    goid_to_go_id = {}
    goid_to_format_name = {}
    goid_to_display_name = {}
    for x in nex_session.query(Go).all():
        goid_to_go_id[x.goid] = x.id
        goid_to_format_name[x.goid] = x.format_name
        goid_to_display_name[x.goid] = x.display_name
        
    for x in bud_session.query(GoSet).all():
        goid = str(x.go.go_go_id)
        while len(goid) < 7:
            goid = '0' + goid
        goid = "GO:" + goid
        go_id = goid_to_go_id.get(goid)
        if go_id is None:
            print "The goid ", goid, " is not in GO table."
            continue
        source = 'SGD'
        name = x.name
        if name == 'generic GO-Slim':
            name = 'Generic GO-Slim'
            source = 'GOC'
        yield { "source": { "display_name": source },
                "bud_id": x.id,
                "go_id": go_id,
                "slim_name": name,
                "display_name": goid_to_display_name[goid],
                "format_name": name.replace(' ', '_') + "_" + goid_to_format_name[goid],
                "link": "/goslim/" + goid,
                "genome_count": x.genome_count,
                'date_created': str(x.date_created),
                'created_by': x.created_by }

    bud_session.close()

   
def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, goslim_starter, 'goslim', lambda x: (x['go_id'], x['slim_name'], x['genome_count'], x['display_name']))


