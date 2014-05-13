from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, OutputTransformer, make_individual_locus_backend_starter, Json2DataPerfDB

__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evidence ------------------------------------------
    from src.sgd.model.nex.evidence import Evidence, Phenotypeevidence
    from src.sgd.convert.from_bud.evidence import make_phenotype_evidence_starter
    do_conversion(make_phenotype_evidence_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Phenotypeevidence),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Phenotypeevidence), name='convert.from_bud.evidence.phenotype', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Phenotypeevidence, Evidence, 'PHENOTYPE')

    # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityDetails

    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioconcept import Phenotype
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    phenotype_ids = [x.id for x in nex_session.query(Phenotype).all()]
    nex_session.close()

    do_conversion(make_individual_locus_backend_starter(nex_backend, 'phenotype_details', 'PHENOTYPE', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PHENOTYPE', name='convert.from_backend.phenotype_details', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])