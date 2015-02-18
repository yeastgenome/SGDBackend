__author__ = 'kpaskov'
import json
from src.sgd.convert.transformers import make_file_starter

def journal_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Journal
    bud_session = bud_session_maker()

    for old_journal in bud_session.query(Journal).all():
        abbreviation = old_journal.abbreviation
        if old_journal.issn == '0948-5023':
            abbreviation = 'J Mol Model (Online)'

        title = old_journal.full_name
        if title is not None or abbreviation is not None:
            yield {'source': {'format_name': 'PubMed'},
                   'title': title,
                   'med_abbr': abbreviation,
                   'issn_print': old_journal.issn,
                   'issn_online': old_journal.essn,
                   'bud_id': old_journal.id,
                   'date_created': str(old_journal.date_created),
                   'created_by': old_journal.created_by}

    bud_session.close()

if __name__ == '__main__':

    from src.sgd.backend.curate import CurateBackend
    from src.sgd.model import bud
    from src.sgd.convert import config
    from src.sgd.convert import prepare_schema_connection

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    curate_backend = CurateBackend(config.NEX_DBTYPE, 'curator-dev-db', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.log_directory)

    accumulated_status = dict()
    for obj_json in journal_starter(bud_session_maker):
        output = curate_backend.update_object('journal', None, obj_json, allow_update_for_add=True)
        status = json.loads(output)['status']
        if status == 'Error':
            print output
        if status not in accumulated_status:
            accumulated_status[status] = 0
        accumulated_status[status] += 1
    print 'convert.journal', accumulated_status

