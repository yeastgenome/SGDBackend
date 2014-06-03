from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Evidence2NexDB, Json2Obj, OutputTransformer, Json2DataPerfDB, \
    make_locus_data_backend_starter, make_reference_data_backend_starter

__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    # perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    # nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evidence ------------------------------------------
    from src.sgd.model.nex.evidence import Evidence, Literatureevidence
    from src.sgd.convert.from_bud.evidence import make_literature_evidence_starter
    do_conversion(make_literature_evidence_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Literatureevidence),
                   Evidence2NexDB(nex_session_maker, lambda x: x.query(Literatureevidence), name='convert.from_bud.evidence.literature', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Literatureevidence, Evidence, 'LITERATURE')

    # # ------------------------------------------ Perf ------------------------------------------
    # from src.sgd.model.perf.bioentity_data import BioentityDetails
    # from src.sgd.model.perf.reference_data import ReferenceDetails
    #
    # from src.sgd.model.nex.bioentity import Locus
    # from src.sgd.model.nex.reference import Reference
    # nex_session = nex_session_maker()
    # locus_ids = [x.id for x in nex_session.query(Locus).all()]
    # reference_ids = [x.id for x in nex_session.query(Reference).all()]
    # nex_session.close()
    #
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'literature_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'LITERATURE', locus_ids, name='convert.from_backend.literature_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_reference_data_backend_starter(nex_backend, 'literature_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'LITERATURE', reference_ids, name='convert.from_backend.literature_details', commit_interval=1000),
    #                 OutputTransformer(1000)])