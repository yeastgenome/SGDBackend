from src.sgd.convert import basic_convert

__author__ = 'sweng99'


def dbuser_starter(bud_session_maker):
    from src.sgd.model.bud.dbuser import Dbuser 
 
    bud_session = bud_session_maker()

    not_curator_list = ['KKARRA', 'GAIL', 'CHERRY', 'SHUAI', 'OTTO', 'VIVIAN',
                        'MKALOPER', 'QDONG', 'MAYANK', 'HITZ', 'GUEST', 'KPASKOV',
                        'PEDROH', 'TSHEPP']

    for bud_obj in bud_session.query(Dbuser).all():

        is_curator = 1
        if bud_obj.username in not_curator_list:
            is_curator = 0
        yield {"username": bud_obj.username,
               "first_name": bud_obj.first_name,
               "last_name": bud_obj.last_name,
               "status": bud_obj.status,
               "email": bud_obj.email,
               "bud_id": bud_obj.id,
               "is_curator": is_curator,
               "date_created": str(bud_obj.date_created)}
         
    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dbuser_starter, 'dbuser', lambda x: x['username'])
    



