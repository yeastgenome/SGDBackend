from src.sgd.model import nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config
from src.sgd.convert.transformers import do_conversion, Json2DataPerfDB, \
    make_locus_data_backend_starter, make_reference_data_backend_starter, make_go_data_backend_starter, \
    make_go_data_with_children_backend_starter, make_ecnumber_data_backend_starter, make_domain_data_backend_starter, \
    make_phenotype_data_backend_starter, make_observable_data_backend_starter, make_chemical_data_backend_starter, make_observable_data_with_children_backend_starter

__author__ = 'kpaskov'

if __name__ == "__main__":

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    from src.sgd.model.perf.bioentity_data import BioentityDetails
    from src.sgd.model.perf.bioconcept_data import BioconceptDetails
    from src.sgd.model.perf.reference_data import ReferenceDetails
    from src.sgd.model.perf.bioitem_data import BioitemDetails

    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.bioconcept import Go, ECNumber, Phenotype, Observable
    from src.sgd.model.nex.bioitem import Domain, Chemical

    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    reference_ids = [x.id for x in nex_session.query(Reference).all()]
    phenotype_ids = [x.id for x in nex_session.query(Phenotype).all()]
    observable_ids = [x.id for x in nex_session.query(Observable).all()]
    chemical_ids = [x.id for x in nex_session.query(Chemical).all()]
    nex_session.close()

    # ------------------------------------------ Literature Perf ------------------------------------------
    do_conversion(make_locus_data_backend_starter(nex_backend, 'literature_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'LITERATURE', locus_ids, name='convert.from_backend.literature_details', commit_interval=1000)])

    do_conversion(make_reference_data_backend_starter(nex_backend, 'literature_details', reference_ids),
                   [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'LITERATURE', reference_ids, name='convert.from_backend.literature_details', commit_interval=1000)])

    # ------------------------------------------ Phenotype Perf ------------------------------------------
    do_conversion(make_locus_data_backend_starter(nex_backend, 'phenotype_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PHENOTYPE', locus_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])

    do_conversion(make_phenotype_data_backend_starter(nex_backend, 'phenotype_details', phenotype_ids),
                   [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'PHENOTYPE_LOCUS', phenotype_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])

    do_conversion(make_reference_data_backend_starter(nex_backend, 'phenotype_details', reference_ids),
                   [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'PHENOTYPE', reference_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])

    do_conversion(make_chemical_data_backend_starter(nex_backend, 'phenotype_details', chemical_ids),
                   [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'PHENOTYPE', chemical_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])

    do_conversion(make_observable_data_backend_starter(nex_backend, 'phenotype_details', observable_ids),
                   [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'OBSERVABLE_LOCUS', observable_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])

    do_conversion(make_observable_data_with_children_backend_starter(nex_backend, 'phenotype_details', observable_ids),
                   [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'OBSERVABLE_LOCUS_ALL_CHILDREN', observable_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])

    # # ------------------------------------------  Literature Perf2 ------------------------------------------
    # perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    # perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)
    #
    # do_conversion(make_locus_data_backend_starter(perf_backend, 'literature_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'LITERATURE', locus_ids, name='convert.from_backend.literature_details', commit_interval=1000)])
    #
    # do_conversion(make_reference_data_backend_starter(perf_backend, 'literature_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'LITERATURE', reference_ids, name='convert.from_backend.literature_details', commit_interval=1000)])
    #
    # # ------------------------------------------ Phenotype Perf2 ------------------------------------------
    # do_conversion(make_locus_data_backend_starter(perf_backend, 'phenotype_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PHENOTYPE', locus_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])
    #
    # do_conversion(make_phenotype_data_backend_starter(perf_backend, 'phenotype_details', phenotype_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'PHENOTYPE_LOCUS', phenotype_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])
    #
    # do_conversion(make_reference_data_backend_starter(perf_backend, 'phenotype_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'PHENOTYPE', reference_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])
    #
    # do_conversion(make_chemical_data_backend_starter(perf_backend, 'phenotype_details', chemical_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'PHENOTYPE', chemical_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])
    #
    # do_conversion(make_observable_data_backend_starter(perf_backend, 'phenotype_details', observable_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'OBSERVABLE_LOCUS', observable_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])
    #
    # do_conversion(make_observable_data_with_children_backend_starter(perf_backend, 'phenotype_details', observable_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'OBSERVABLE_LOCUS_ALL_CHILDREN', observable_ids, name='convert.from_backend.phenotype_details', commit_interval=1000)])