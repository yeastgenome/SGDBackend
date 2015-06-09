from sqlalchemy.orm import joinedload
from src.sgd.convert.into_curate import basic_convert, remove_nones
from src.sgd.convert.into_curate.keyword import keyword_mapping

__author__ = 'kpaskov'


def load_urls(bud_colleague, bud_session):
    from src.sgd.model.bud.colleague import ColleagueUrl

    urls = []

    for bud_obj in bud_session.query(ColleagueUrl).options(joinedload('url')).filter_by(colleague_id=bud_colleague.id).all():
        urls.append(
            {'name': bud_obj.url.url_type,
             'source': {'name': bud_obj.url.source},
             'bud_id': bud_obj.id,
             'link': bud_obj.url.url,
             'url_type': bud_obj.url.url_type,
             'date_created': str(bud_obj.url.date_created),
             'created_by': bud_obj.url.created_by})

    make_unique = dict([((x['name'], x['url_type']), x) for x in urls])
    return make_unique.values()


def load_documents(bud_colleague, bud_session):
    from src.sgd.model.bud.colleague import ColleagueRemark, ColleagueKeyword

    documents = []
    text = ' '.join([x.remark for x in bud_session.query(ColleagueRemark).filter_by(colleague_id=bud_colleague.id).filter_by(remark_type='Research Interest').all()])
    text += '\n'
    text += ', '.join([x.remark for x in bud_session.query(ColleagueRemark).filter_by(colleague_id=bud_colleague.id).filter_by(remark_type='Announcement').all()])
    text += ', '.join([x.keyword.keyword for x in bud_session.query(ColleagueKeyword).options(joinedload('keyword')).filter_by(colleague_id=bud_colleague.id).all() if x.keyword.source == 'Colleague Keyword'])

    text = text.strip()

    if text != '':
        documents.append(
            {'text': text,
             'html': text,
             'source': {'name': 'SGD'},
             'bud_id': bud_colleague.id,
             'document_type': 'Research Interest',
             'date_created': str(bud_colleague.date_created),
             'created_by': bud_colleague.created_by})

    return documents


def load_keywords(bud_colleague, bud_session):
    from src.sgd.model.bud.colleague import ColleagueKeyword

    keywords = []

    for bud_obj in bud_session.query(ColleagueKeyword).options(joinedload('keyword')).filter_by(colleague_id=bud_colleague.id).all():
        if bud_obj.keyword.source == 'Curator-defined':
            keywords.append(
                {'name': bud_obj.keyword.keyword if bud_obj.keyword.keyword not in keyword_mapping else keyword_mapping[bud_obj.keyword.keyword],
                 'source': {'name': bud_obj.keyword.source},
                 'bud_id': bud_obj.id,
                 'date_created': str(bud_obj.keyword.date_created),
                 'created_by': bud_obj.keyword.created_by})

    return keywords


def load_loci(bud_colleague, bud_session):
    from src.sgd.model.bud.colleague import ColleagueFeature
    return [{'systematic_name': x.feature.name} for x in bud_session.query(ColleagueFeature).options(joinedload('feature')).filter_by(colleague_id=bud_colleague.id).all()]


def load_relations(bud_colleague, bud_session):
    from src.sgd.model.bud.colleague import ColleagueRelation
    return [{"email": x.associate.email,
             "first_name": x.associate.first_name,
             "last_name": x.associate.last_name,
             "relation_type": x.relationship_type,
             "source": {"name": "SGD"}} for x in bud_session.query(ColleagueRelation).options(joinedload('associate')).filter_by(colleague_id=bud_colleague.id).all()]


def colleague_starter(bud_session_maker):
    from src.sgd.model.bud.colleague import Colleague

    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(Colleague).all():
        if bud_obj.email is not None:
            obj_json = remove_nones({
                'bud_id': bud_obj.id,
                'source': {'name': bud_obj.source},
                'last_name': bud_obj.last_name,
                'first_name': bud_obj.first_name,
                'other_last_name': bud_obj.other_last_name,
                'job_title': bud_obj.job_title,
                'institution': bud_obj.institution,
                'address1': bud_obj.address1,
                'address2': bud_obj.address2,
                'address3': bud_obj.address3,
                'city': bud_obj.city,
                'country': bud_obj.country,
                'work_phone': bud_obj.work_phone,
                'other_phone': bud_obj.other_phone,
                'fax': bud_obj.fax,
                'email': bud_obj.email,
                'is_pi': True if bud_obj.is_pi == 'Y' else False,
                'is_contact': True if bud_obj.is_contact == 'Y' else False,
                'display_email': True if bud_obj.display_email == 'Y' else False,
                'suffix': bud_obj.suffix,
                'state': bud_obj.state if bud_obj.state is not None else bud_obj.region,
                'profession': bud_obj.profession,
                'date_last_modified': str(bud_obj.date_last_modified),
                'date_created': str(bud_obj.date_created),
                'created_by': bud_obj.created_by})

            #Load urls
            obj_json['urls'] = load_urls(bud_obj, bud_session)

            #Load documents
            obj_json['documents'] = load_documents(bud_obj, bud_session)

            #Load keywords
            obj_json['keywords'] = load_keywords(bud_obj, bud_session)

            #Load loci
            #obj_json['locuses'] = load_loci(bud_obj, bud_session)

            #Load children
            obj_json['children'] = load_relations(bud_obj, bud_session)

            yield obj_json

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, colleague_starter, 'colleague', lambda x: x['email'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

