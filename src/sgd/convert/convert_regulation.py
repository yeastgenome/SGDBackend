from src.sgd.model import nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Evidence2NexDB, Json2Obj, OutputTransformer, \
    make_locus_data_backend_starter, make_reference_data_backend_starter, Json2DataPerfDB
__author__ = 'kpaskov'

if __name__ == "__main__":

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evidence ------------------------------------------
    from src.sgd.model.nex.evidence import Evidence, Regulationevidence
    from src.sgd.convert.from_bud.evidence import make_regulation_evidence_starter
    do_conversion(make_regulation_evidence_starter(nex_session_maker),
                  [Json2Obj(Regulationevidence),
                   Evidence2NexDB(nex_session_maker, lambda x: x.query(Regulationevidence), name='convert.from_bud.evidence.regulation', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Regulationevidence, Evidence, 'REGULATION')

    # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityDetails, BioentityEnrichment
    from src.sgd.model.perf.reference_data import ReferenceDetails

    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.reference import Reference
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    reference_ids = [x.id for x in nex_session.query(Reference).all()]
    nex_session.close()

    do_conversion(make_locus_data_backend_starter(nex_backend, 'regulation_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'REGULATION', locus_ids, name='convert.from_backend.regulation_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_reference_data_backend_starter(nex_backend, 'regulation_details', reference_ids),
                   [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'REGULATION', reference_ids, name='convert.from_backend.regulation_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_locus_data_backend_starter(nex_backend, 'regulation_target_enrichment', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityEnrichment, 'REGULATION', locus_ids, name='convert.from_backend.regulation_target_enrichment', commit_interval=1000),
                    OutputTransformer(1000)])

    # ------------------------------------------ Perf2 ------------------------------------------
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)

    do_conversion(make_locus_data_backend_starter(perf_backend, 'regulation_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'REGULATION', locus_ids, name='convert.from_backend.regulation_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_reference_data_backend_starter(perf_backend, 'regulation_details', reference_ids),
                   [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'REGULATION', reference_ids, name='convert.from_backend.regulation_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_locus_data_backend_starter(perf_backend, 'regulation_target_enrichment', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityEnrichment, 'REGULATION', locus_ids, name='convert.from_backend.regulation_target_enrichment', commit_interval=1000),
                    OutputTransformer(1000)])
