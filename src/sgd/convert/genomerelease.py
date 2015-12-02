from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

def genomerelease_starter(bud_session_maker):
    from src.sgd.model.bud.sequence import Release
    bud_session = bud_session_maker()

    for x in bud_session.query(Release).all():

        yield remove_nones({
                'source': {'display_name': 'SGD'},
                'display_name': x.genome_release,
                'format_name': x.genome_release,
                'bud_id': x.id,   
                'sequence_release': x.sequence_release,
                'annotation_release': x.annotation_release,
                'curation_release': x.curation_release,
                'release_date': str(x.release_date),
                'date_created': str(x.date_created),
                'created_by': x.created_by})

    bud_session.close()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, genomerelease_starter, 'genomerelease', lambda x: x['display_name'])



