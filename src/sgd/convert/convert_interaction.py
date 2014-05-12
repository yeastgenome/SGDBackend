from src.sgd.convert import config

__author__ = 'kpaskov'

if __name__ == "__main__":   

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf1_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    perf2_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    from src.sgd.model.nex.evidence import Geninteractionevidence, Physinteractionevidence
    do_conversion(make_interaction_evidence_starter(bud_session_maker, nex_session_maker, 'genetic interactions'),
                  [Json2Obj(Geninteractionevidence),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Geninteractionevidence), name='convert.from_bud.evidence.geninteraction', delete_untouched=True),
                   OutputTransformer(1000)])

    do_conversion(make_interaction_evidence_starter(bud_session_maker, nex_session_maker, 'physical interactions'),
                  [Json2Obj(Physinteractionevidence),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Physinteractionevidence), name='convert.from_bud.evidence.physinteraction', delete_untouched=True),
                   OutputTransformer(1000)])

