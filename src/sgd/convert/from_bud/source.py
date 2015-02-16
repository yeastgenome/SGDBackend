__author__ = 'kpaskov'
import json

other_sources = ['SGD', 'GO', 'PROSITE', 'Gene3D', 'SUPERFAMILY', 'TIGRFAM', 'Pfam', 'PRINTS',
                                        'PIRSF', 'JASPAR', 'SMART', 'PANTHER', 'ProDom', 'DOI',
                                        'PubMedCentral', 'PubMed', '-', 'ECO', 'TMHMM', 'SignalP', 'PhosphoGRID',
                                        'GenBank/EMBL/DDBJ', 'Phobius']

ok_codes = {('ALIAS', 'ALIAS_TYPE'), ('DBXREF', 'SOURCE'), ('EXPERIMENT', 'SOURCE'), ('FEATURE', 'SOURCE'),
                ('GO_ANNOTATION', 'SOURCE'), ('HOMOLOG', 'SOURCE'), ('INTERACTION', 'SOURCE'), ('PHENOTYPE', 'SOURCE'),
                ('REFTYPE', 'SOURCE'), ('REFERENCE', 'SOURCE'), ('URL', 'SOURCE')}

def source_starter(bud_session_maker):
    from src.sgd.model.bud.cv import Code
    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(Code).all():
        if (bud_obj.tab_name, bud_obj.col_name) in ok_codes:
            obj_json = {'display_name': bud_obj.code_value,
                        'bud_id': bud_obj.id,
                        'date_created': str(bud_obj.date_created),
                        'created_by': bud_obj.created_by}

            if bud_obj.description is not None:
                obj_json['description'] = bud_obj.description

            yield obj_json

    for source in other_sources:
        yield {'display_name': source}

    bud_session.close()

if __name__ == '__main__':

    from src.sgd.backend.curate import CurateBackend
    from src.sgd.model import bud
    from src.sgd.convert import config
    from src.sgd.convert import prepare_schema_connection

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    curate_backend = CurateBackend(config.NEX_DBTYPE, 'curator-dev-db', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.log_directory)

    accumulated_status = dict()
    for obj_json in source_starter(bud_session_maker):
        status = json.loads(curate_backend.update_object('source', None, obj_json))['status']
        if status not in accumulated_status:
            accumulated_status[status] = 0
        accumulated_status[status] += 1
    print 'convert.source', accumulated_status

