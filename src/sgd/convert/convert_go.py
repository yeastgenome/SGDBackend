from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Json2Obj, OutputTransformer, Json2DataPerfDB, \
    make_locus_data_backend_starter, make_reference_data_backend_starter, make_go_data_backend_starter, Evidence2NexDB, make_go_data_with_children_backend_starter

__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # # ------------------------------------------ Evidence ------------------------------------------
    # from src.sgd.model.nex.evidence import Evidence, Goevidence
    # from src.sgd.convert.from_bud.evidence import make_go_evidence_starter
    # do_conversion(make_go_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Goevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(Goevidence), name='convert.from_bud.evidence.go', delete_untouched=True, commit_interval=1000),
    #                 OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Goevidence, Evidence, 'GO')
    #
    # # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityDetails
    from src.sgd.model.perf.bioconcept_data import BioconceptDetails
    from src.sgd.model.perf.reference_data import ReferenceDetails

    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioconcept import Go
    from src.sgd.model.nex.reference import Reference
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    go_ids = [x.id for x in nex_session.query(Go).all()]
    reference_ids = [x.id for x in nex_session.query(Reference).all()]
    nex_session.close()
    #
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'go_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'GO', locus_ids, name='convert.from_backend.go_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_go_data_backend_starter(nex_backend, 'go_details', go_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'GO_LOCUS', go_ids, name='convert.from_backend.go_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_reference_data_backend_starter(nex_backend, 'go_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'GO', reference_ids, name='convert.from_backend.go_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_go_data_with_children_backend_starter(nex_backend, 'go_details', go_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'GO_LOCUS_ALL_CHILDREN', go_ids, name='convert.from_backend.go_details', commit_interval=1000),
    #                 OutputTransformer(1000)])

    # ------------------------------------------ Perf2 ------------------------------------------
    perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    do_conversion(make_locus_data_backend_starter(perf_backend, 'go_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'GO', locus_ids, name='convert.from_backend.go_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_go_data_backend_starter(perf_backend, 'go_details', go_ids),
                   [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'GO_LOCUS', go_ids, name='convert.from_backend.go_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_reference_data_backend_starter(perf_backend, 'go_details', reference_ids),
                   [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'GO', reference_ids, name='convert.from_backend.go_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_go_data_with_children_backend_starter(perf_backend, 'go_details', go_ids),
                   [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'GO_LOCUS_ALL_CHILDREN', go_ids, name='convert.from_backend.go_details', commit_interval=1000),
                    OutputTransformer(1000)])