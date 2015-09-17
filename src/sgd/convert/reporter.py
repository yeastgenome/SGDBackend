from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def reporter_starter(bud_session_maker):
    from src.sgd.model.bud.phenotype import ExperimentProperty

    bud_session = bud_session_maker()
    
    for bud_obj in bud_session.query(ExperimentProperty).all():
        if bud_obj.type == 'Reporter':
            desc = ''
            if bud_obj.description is not None:
                desc = bud_obj.description
            obj_json = {
                'source': {'display_name': 'SGD'},
                'display_name': bud_obj.value,
                'description': desc,    
                'bud_id': bud_obj.id,
                'date_created': str(bud_obj.date_created),
                'created_by': bud_obj.created_by
            }
            yield obj_json

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, reporter_starter, 'reporter', lambda x: x['display_name'])


