from sqlalchemy.orm import joinedload
from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'


def colleague_starter(bud_session_maker):
    from src.sgd.model.bud.colleague import Colleague, ColleagueKeyword, ColleagueRemark
    from src.sgd.model.bud.general import NoteFeat

    bud_session = bud_session_maker()

    ## get research interests from BUD
    
    interests = {}
    for kw_obj in bud_session.query(ColleagueKeyword).all():
        if kw_obj.keyword.source != 'Colleague Keyword':
            continue
        coll_id = kw_obj.colleague_id
        if coll_id in interests:
            interests[coll_id] = interests[coll_id] + ', ' + kw_obj.keyword.keyword
        else:
            interests[coll_id] = kw_obj.keyword.keyword
    
    for r_obj in bud_session.query(ColleagueRemark).all():
        if r_obj.remark_type not in ['Research Interest', 'Announcement']:
            continue
        coll_id = r_obj.colleague_id
        if coll_id in interests:
            interests[coll_id] = interests[coll_id] + ', ' + r_obj.remark
        else:
            interests[coll_id] = r_obj.remark

    coll_id_to_note = {}
    for x in bud_session.query(NoteFeat).filter_by(tab_name='COLLEAGUE').all():
        coll_id_to_note[x.primary_key] = x.note.note
    
    for bud_obj in bud_session.query(Colleague).all():

        # print "research_interest: ", interests.get(bud_obj.id), "\n"

        obj_json = remove_nones({
            'bud_id': bud_obj.id,
            'source': {'display_name': 'Direct submission'},
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
            'research_interest': interests.get(bud_obj.id),
            'postal_code': bud_obj.postal_code,
            'date_last_modified': str(bud_obj.date_last_modified),
            'date_created': str(bud_obj.date_created),
            'created_by': bud_obj.created_by})

        if coll_id_to_note.get(bud_obj.id) is not None:
            obj_json['colleague_note'] = coll_id_to_note.get(bud_obj.id)

            print "COLLEAGUE_NOTE: ", coll_id_to_note.get(bud_obj.id)

        yield obj_json

    bud_session.close()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, colleague_starter, 'colleague', lambda x: (x['first_name'], x['last_name'], x['bud_id']))

