from src.sgd.model import nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, OutputTransformer, \
    make_individual_locus_backend_starter, Json2DataPerfDB
__author__ = 'kpaskov'

if __name__ == "__main__":

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evidence ------------------------------------------
    from src.sgd.model.nex.evidence import Evidence, Regulationevidence
    from src.sgd.convert.from_bud.evidence import make_regulation_evidence_starter
    do_conversion(make_regulation_evidence_starter(nex_session_maker),
                  [Json2Obj(Regulationevidence),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Regulationevidence), name='convert.from_bud.evidence.regulation', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Regulationevidence, Evidence, 'REGULATION')

    # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityDetails

    from src.sgd.model.nex.bioentity import Locus
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    nex_session.close()

    do_conversion(make_individual_locus_backend_starter(nex_backend, 'regulation_details', 'REGULATION', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'REGULATION', name='convert.from_backend.regulation_details', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])