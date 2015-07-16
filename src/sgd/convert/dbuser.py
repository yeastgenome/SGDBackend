from src.sgd.convert import basic_convert

__author__ = 'sweng99'


def dbuser_starter(bud_session_maker):
    from src.sgd.model.bud.dbuser import Dbuser 
 
    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(Dbuser).all():

        yield {"username": bud_obj.username,
               "first_name": bud_obj.first_name,
               "last_name": bud_obj.last_name,
               "status": bud_obj.status,
               "email": bud_obj.email,
               "bud_id": bud_obj.id,
               "date_created": str(bud_obj.date_created)}
         
    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dbuser_starter, 'dbuser', lambda x: x['username'])
    



