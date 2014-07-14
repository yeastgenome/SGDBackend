from src.sgd.model import nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config
from src.sgd.convert.transformers import do_conversion, \
    make_backend_starter, Json2CorePerfDB, Json2OrphanPerfDB, Json2DisambigPerfDB, make_orphan_backend_starter


__author__ = 'kpaskov'

if __name__ == "__main__":   

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Perf ------------------------------------------

    # ------------------------------------------ Reference ------------------------------------------
    from src.sgd.model.perf.core import Reference as PerfReference, Author as PerfAuthor, Bibentry as PerfBibentry
    do_conversion(make_backend_starter(nex_backend, 'all_references', 1000),
                  [Json2CorePerfDB(perf_session_maker, PerfReference, name='convert.from_backend.reference', delete_untouched=True, commit_interval=1000)])

    # do_conversion(make_backend_starter(nex_backend, 'all_authors', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfAuthor, name='convert.from_backend.author', delete_untouched=True, commit_interval=1000)])
    #
    # do_conversion(make_backend_starter(nex_backend, 'all_bibentries', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBibentry, name='convert.from_backend.all_bibentries', commit_interval=1000, delete_untouched=True)])
    #
    # do_conversion(make_orphan_backend_starter(nex_backend, ['references_this_week']),
    #                [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])
    #
    # # ------------------------------------------ Perf2 ------------------------------------------
    # perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    # perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)
    #
    # # ------------------------------------------ Reference ------------------------------------------
    # from src.sgd.model.perf.core import Reference as PerfReference, Author as PerfAuthor, Bibentry as PerfBibentry
    # do_conversion(make_backend_starter(perf_backend, 'all_references', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfReference, name='convert.from_backend.reference', delete_untouched=True, commit_interval=1000)])
    #
    # do_conversion(make_backend_starter(perf_backend, 'all_authors', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfAuthor, name='convert.from_backend.author', delete_untouched=True, commit_interval=1000)])
    #
    # do_conversion(make_backend_starter(perf_backend, 'all_bibentries', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBibentry, name='convert.from_backend.all_bibentries', commit_interval=1000, delete_untouched=True)])
    #
    # do_conversion(make_orphan_backend_starter(perf_backend, ['references_this_week']),
    #                [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])
    #
    #
    #
    #
