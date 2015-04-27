from src.sgd.model import nex, perf, bud
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, OutputTransformer, make_locus_data_backend_starter, \
    Json2DataPerfDB, make_orphan_backend_starter, Json2OrphanPerfDB

__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evidence ------------------------------------------
    from src.sgd.model.nex.evidence import Alignmentevidence
    from src.sgd.convert.from_bud.evidence import make_alignment_evidence_starter

    do_conversion(make_alignment_evidence_starter(nex_session_maker),
                      [Json2Obj(Alignmentevidence),
                       Obj2NexDB(nex_session_maker, lambda x: x.query(Alignmentevidence),
                                 name='convert.from_bud.evidence.alignment_evidence',
                                 delete_untouched=True,
                                 commit_interval=1000),
                       OutputTransformer(1000)])


    # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityDetails

    from src.sgd.model.nex.bioentity import Locus
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    nex_session.close()

    do_conversion(make_locus_data_backend_starter(nex_backend, 'alignment_bioent', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'ALIGNMENT', locus_ids, name='convert.from_backend.alignment_details', commit_interval=10),
                    OutputTransformer(100)])

    do_conversion(make_orphan_backend_starter(nex_backend, ['alignments']),
                  [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])

    # ------------------------------------------ Perf2 ------------------------------------------
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)

    do_conversion(make_locus_data_backend_starter(perf_backend, 'alignment_bioent', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'ALIGNMENT', locus_ids, name='convert.from_backend.alignment_details', commit_interval=10),
                    OutputTransformer(100)])

    do_conversion(make_orphan_backend_starter(perf_backend, ['alignments']),
                  [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])
