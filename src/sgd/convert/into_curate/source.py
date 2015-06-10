from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'

other_sources = ['SGD', 'GO', 'PROSITE', 'Gene3D', 'SUPERFAMILY', 'TIGRFAM', 'Pfam', 'PRINTS',
                                        'PIRSF', 'JASPAR', 'SMART', 'PANTHER', 'ProDom', 'DOI',
                                        'PubMedCentral', 'PubMed', '-', 'ECO', 'TMHMM', 'SignalP', 'PhosphoGRID',
                                        'GenBank/EMBL/DDBJ', 'Phobius', 'SO']

ok_codes = {('ALIAS', 'ALIAS_TYPE'), ('DBXREF', 'SOURCE'), ('EXPERIMENT', 'SOURCE'), ('FEATURE', 'SOURCE'),
                ('GO_ANNOTATION', 'SOURCE'), ('HOMOLOG', 'SOURCE'), ('INTERACTION', 'SOURCE'), ('PHENOTYPE', 'SOURCE'),
                ('REFTYPE', 'SOURCE'), ('REFERENCE', 'SOURCE'), ('URL', 'SOURCE')}


def source_starter(bud_session_maker):
    from src.sgd.model.bud.cv import Code
    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(Code).all():
        if (bud_obj.tab_name, bud_obj.col_name) in ok_codes and bud_obj.code_value != 'Publication':
            obj_json = {'name': bud_obj.code_value,
                        'bud_id': bud_obj.id,
                        'date_created': str(bud_obj.date_created),
                        'created_by': bud_obj.created_by}

            if bud_obj.description is not None:
                obj_json['description'] = bud_obj.description

            yield obj_json

    for source in other_sources:
        yield {'name': source}

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, source_starter, 'source', lambda x: x['name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

