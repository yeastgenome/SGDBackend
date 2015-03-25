from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Json2Obj, OutputTransformer, Evidence2NexDB, make_locus_data_backend_starter, Json2DataPerfDB
__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    from src.sgd.model.nex.evidence import Posttranslationalevidence, Evidence
    from src.sgd.convert.from_bud.evidence import make_posttranslational_evidence_starter

    do_conversion(make_posttranslational_evidence_starter(nex_session_maker),
                  [Json2Obj(Posttranslationalevidence),
                   Evidence2NexDB(nex_session_maker, lambda x: x.query(Posttranslationalevidence),
                                  name='convert.from_bud.evidence.posttranslationsl',
                                  delete_untouched=True,
                                  commit_interval=1000,
                                  already_deleted=clean_up_orphans(nex_session_maker, Posttranslationalevidence, Evidence, 'POSTTRANSLATIONAL')),
                   OutputTransformer(1000)])

    from src.sgd.model.nex.bioentity import Locus
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    nex_session.close()

    from src.sgd.model.perf.bioentity_data import BioentityDetails
    do_conversion(make_locus_data_backend_starter(nex_backend, 'posttranslational_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'POSTTRANSLATIONAL', locus_ids, name='convert.from_backend.posttranslational_details',
                                    commit_interval=1000, delete_untouched=False),
                    OutputTransformer(1000)])

    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)

    do_conversion(make_locus_data_backend_starter(nex_backend, 'posttranslational_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'POSTTRANSLATIONAL', locus_ids, name='convert.from_backend.posttranslational_details',
                                    commit_interval=1000, delete_untouched=False),
                    OutputTransformer(1000)])