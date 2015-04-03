from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, Json2CorePerfDB, make_backend_starter
__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    from src.sgd.model.nex.bioitem import Reservedname
    from src.sgd.model.nex.paragraph import Paragraph, Bioentityparagraph, ParagraphReference
    from src.sgd.convert.from_bud.paragraph import make_bioentity_paragraph_starter, make_paragraph_reference_starter

    do_conversion(make_bioentity_paragraph_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioentityparagraph),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityparagraph),
                             name='convert.from_bud.paragraph.bioentity',
                             delete_untouched=True,
                             commit=True,
                             already_deleted=clean_up_orphans(nex_session_maker, Bioentityparagraph, Paragraph, 'BIOENTITY'))])

    do_conversion(make_paragraph_reference_starter(nex_session_maker),
                  [Json2Obj(ParagraphReference),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(ParagraphReference),
                             name='convert.from_bud.paragraph_reference',
                             delete_untouched=True,
                             commit=True)])

    from src.sgd.model.perf.core import Bioentity as PerfBioentity
    do_conversion(make_backend_starter(nex_backend, 'all_bioentities', 1000),
                  [Json2CorePerfDB(perf_session_maker, PerfBioentity, name='convert.from_backend.bioentity', commit_interval=1000, delete_untouched=True)])

    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)

    do_conversion(make_backend_starter(perf_backend, 'all_bioentities', 1000),
                  [Json2CorePerfDB(perf_session_maker, PerfBioentity, name='convert.from_backend.bioentity', commit_interval=1000, delete_untouched=True)])