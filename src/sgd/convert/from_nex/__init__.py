__author__ = 'kpaskov'

from src.sgd.convert.transformers import make_db_starter

def make_core_starter(nex_session_maker, clss):
    def core_starter():
        nex_session = nex_session_maker()
        for cls in clss:
            for obj in make_db_starter(nex_session.query(cls), 1000)():
                yield obj.to_json()
        nex_session.close()
    return core_starter