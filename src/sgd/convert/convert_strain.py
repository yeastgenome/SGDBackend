from src.sgd.model import bud, nex, perf
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, \
    make_backend_starter, Json2CorePerfDB, Json2Obj, Obj2NexDB
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend


__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evelements ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.misc import Strain, Url, Strainurl
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.convert.from_bud.evelements import make_strain_starter, make_strain_url_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter

    do_conversion(make_strain_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Strain),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Strain),
                             name='convert.from_bud.strain',
                             delete_untouched=True,
                             commit=True)])

    do_conversion(make_strain_url_starter(nex_session_maker),
                  [Json2Obj(Strainurl),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Strainurl),
                             name='convert.from_bud.strain.url',
                             delete_untouched=True,
                             commit_interval=1000,
                             already_deleted=clean_up_orphans(nex_session_maker, Strainurl, Url, 'STRAIN'))])

    do_conversion(make_disambig_starter(nex_session_maker, Strain, ['id', 'format_name'], 'STRAIN', None),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'STRAIN'),
                             name='convert.from_bud.strain.disambig',
                             delete_untouched=True,
                             commit=True)])

    # ------------------------------------------ Paragraph ------------------------------------------
    from src.sgd.model.nex.paragraph import Paragraph, Strainparagraph, ParagraphReference
    from src.sgd.convert.from_bud.paragraph import make_strain_paragraph_starter, make_paragraph_reference_starter

    do_conversion(make_strain_paragraph_starter(nex_session_maker),
                  [Json2Obj(Strainparagraph),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Strainparagraph),
                             name='convert.from_bud.paragraph.strain',
                             delete_untouched=True,
                             commit=True,
                             already_deleted=clean_up_orphans(nex_session_maker, Strainparagraph, Paragraph, 'STRAIN'))])

    # do_conversion(make_paragraph_reference_starter(nex_session_maker),
    #               [Json2Obj(ParagraphReference),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(ParagraphReference),
    #                          name='convert.from_bud.paragraph_reference',
    #                          delete_untouched=True,
    #                          commit=True)])

    # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.core import Strain as PerfStrain
    do_conversion(make_backend_starter(nex_backend, 'all_strains', 1000),
                  [Json2CorePerfDB(perf_session_maker, PerfStrain, name='convert.from_backend.strain', commit_interval=1000, delete_untouched=True)])


    # ------------------------------------------ Perf2 ------------------------------------------
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)

    do_conversion(make_backend_starter(perf_backend, 'all_strains', 1000),
                  [Json2CorePerfDB(perf_session_maker, PerfStrain, name='convert.from_backend.strain', commit_interval=1000, delete_untouched=True)])