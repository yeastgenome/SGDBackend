from src.sgd.convert.into_curate import basic_convert, remove_nones

__author__ = 'kpaskov'


def genomerelease_starter(bud_session_maker):
    from src.sgd.model.bud.sequence import Release

    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(Release).all():
        if bud_obj.genome_release is not None:
            obj_json = remove_nones({
                'bud_id': bud_obj.id,
                'source': {'name': 'SGD'},
                'genome_release': bud_obj.genome_release,
                'sequence_release': bud_obj.sequence_release,
                'annotation_release': bud_obj.annotation_release,
                'curation_release': bud_obj.curation_release,
                'filename': bud_obj.filename,
                'release_date': str(bud_obj.release_date),
                'date_created': str(bud_obj.date_created),
                'created_by': bud_obj.created_by})
            yield obj_json

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, genomerelease_starter, 'genomerelease', lambda x: x['genome_release'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

