from src.sgd.model import nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config
from src.sgd.convert.transformers import do_conversion, \
    make_backend_starter, Json2CorePerfDB, Json2OrphanPerfDB, Json2DisambigPerfDB, make_orphan_arg_backend_starter


__author__ = 'kpaskov'

if __name__ == "__main__":   

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Perf ------------------------------------------

    # # ------------------------------------------ Disambig ------------------------------------------
    # do_conversion(make_backend_starter(nex_backend, 'all_disambigs', 1000),
    #                [Json2DisambigPerfDB(perf_session_maker, commit_interval=1000)])
    #
    # # ------------------------------------------ Evelements ------------------------------------------
    # from src.sgd.model.perf.core import Strain as PerfStrain
    # do_conversion(make_backend_starter(nex_backend, 'all_strains', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfStrain, name='convert.from_backend.strain', commit_interval=1000, delete_untouched=True)])

    # # ------------------------------------------ Bioentity ------------------------------------------
    from src.sgd.model.perf.core import Bioentity as PerfBioentity, Locustab as PerfLocustab, Locusentry as PerfLocusentry, Tag as PerfTag
    # do_conversion(make_backend_starter(nex_backend, 'all_bioentities', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioentity, name='convert.from_backend.bioentity', commit_interval=1000, delete_untouched=True)])

    # do_conversion(make_backend_starter(nex_backend, 'all_locustabs', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfLocustab, name='convert.from_backend.all_locustabs', commit_interval=1000, delete_untouched=True)])
    #
    # do_conversion(make_backend_starter(nex_backend, 'all_locusentries', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfLocusentry, name='convert.from_backend.all_locusentries', commit_interval=1000, delete_untouched=True)])
    #
    # # ------------------------------------------ Bioconcept ------------------------------------------
    # from src.sgd.model.perf.core import Bioconcept as PerfBioconcept
    # do_conversion(make_backend_starter(nex_backend, 'all_bioconcepts', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioconcept, name='convert.from_backend.bioconcept', delete_untouched=True, commit_interval=1000)])
    #
    # # ------------------------------------------ Bioitem ------------------------------------------
    # from src.sgd.model.perf.core import Bioitem as PerfBioitem
    # do_conversion(make_backend_starter(nex_backend, 'all_bioitems', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioitem, name='convert.from_backend.bioitem', commit_interval=1000, delete_untouched=True)])
    #
    # ------------------------------------------ Tag ------------------------------------------
    do_conversion(make_backend_starter(nex_backend, 'all_tags', 1000),
                  [Json2CorePerfDB(perf_session_maker, PerfTag, name='convert.from_backend.tag', commit_interval=1000, delete_untouched=True)])

    do_conversion(make_orphan_arg_backend_starter(nex_backend, 'obj_list', ['tag']),
                   [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])

    # # ------------------------------------------ Perf2 ------------------------------------------
    # perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    # perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)
    #
    # # ------------------------------------------ Disambig ------------------------------------------
    # do_conversion(make_backend_starter(perf_backend, 'all_disambigs', 1000),
    #                [Json2DisambigPerfDB(perf_session_maker, commit_interval=1000)])
    #
    # # ------------------------------------------ Evelements ------------------------------------------
    # from src.sgd.model.perf.core import Strain as PerfStrain
    # do_conversion(make_backend_starter(perf_backend, 'all_strains', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfStrain, name='convert.from_backend.strain', commit_interval=1000, delete_untouched=True)])
    #
    # # ------------------------------------------ Bioentity ------------------------------------------
    # from src.sgd.model.perf.core import Bioentity as PerfBioentity, Locustab as PerfLocustab, Locusentry as PerfLocusentry
    # do_conversion(make_backend_starter(perf_backend, 'all_bioentities', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioentity, name='convert.from_backend.bioentity', commit_interval=1000, delete_untouched=True)])
    #
    # do_conversion(make_backend_starter(perf_backend, 'all_locustabs', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfLocustab, name='convert.from_backend.all_locustabs', commit_interval=1000, delete_untouched=True)])
    #
    # do_conversion(make_backend_starter(perf_backend, 'all_locusentries', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfLocusentry, name='convert.from_backend.all_locusentries', commit_interval=1000, delete_untouched=True)])
    #
    # # ------------------------------------------ Bioconcept ------------------------------------------
    # from src.sgd.model.perf.core import Bioconcept as PerfBioconcept
    # do_conversion(make_backend_starter(perf_backend, 'all_bioconcepts', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioconcept, name='convert.from_backend.bioconcept', delete_untouched=True, commit_interval=1000)])
    #
    # # ------------------------------------------ Bioitem ------------------------------------------
    # from src.sgd.model.perf.core import Bioitem as PerfBioitem
    # do_conversion(make_backend_starter(perf_backend, 'all_bioitems', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioitem, name='convert.from_backend.bioitem', commit_interval=1000, delete_untouched=True)])
    #
    # # ------------------------------------------ Tag ------------------------------------------
    # do_conversion(make_backend_starter(perf_backend, 'all_tags', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfTag, name='convert.from_backend.tag', commit_interval=1000, delete_untouched=True)])
    #
    # do_conversion(make_orphan_arg_backend_starter(perf_backend, 'obj_list', ['tag']),
    #                [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])
