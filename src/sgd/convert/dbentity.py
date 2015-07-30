from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

def dbentity_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Reference
    from src.sgd.model.bud.feature import Feature
    bud_session = bud_session_maker()

    print "loading LOCUS data..."

    for locus in bud_session.query(Feature).all():
        yield {'source': {'display_name': 'SGD'},
               'sgdid': locus.dbxref_id,
               'display_name': locus.gene_name if locus.gene_name != None else locus.name,
               'format_name': locus.name,
               'class_type': 'LOCUS',
               'dbentity_status': locus.status,
               'bud_id': locus.id,
               'date_created': str(locus.date_created),
               'created_by': locus.created_by}

    print "loading REFERENCE data..."

    for ref in bud_session.query(Reference).all():
        source = 'SGD'
        if 'PubMed' in ref.source:
            source = 'NCBI'
        elif 'PDB' in ref.source:
            source = 'PDB'
        elif 'YPD' in ref.source:
            source = 'YPD'
        yield {'source': {'display_name': source},
               'sgdid': ref.dbxref_id,
               'display_name': ref.citation.split(')')[0] + ')',
               'class_type': 'REFERENCE',
               'dbentity_status': 'Active',
               'bud_id': ref.id,
               'date_created': str(ref.date_created),
               'created_by': ref.created_by}

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dbentity_starter, 'dbentity', lambda x: x['display_name'])




