from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Evidence2NexDB, Json2Obj, OutputTransformer, Json2DataPerfDB, \
    make_locus_data_backend_starter, make_ecnumber_data_backend_starter, make_domain_data_backend_starter


__author__ = 'kpaskov'

if __name__ == "__main__":   

    # bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # # ------------------------------------------ Evidence ------------------------------------------
    # # Bud -> Nex
    # from src.sgd.model.nex.evidence import Evidence, Domainevidence, Bindingevidence, Phosphorylationevidence, \
    #     ECNumberevidence, Proteinexperimentevidence, Aliasevidence
    # from src.sgd.convert.from_bud.evidence import make_domain_evidence_starter, make_protein_experiment_evidence_starter, \
    #     make_ecnumber_evidence_starter, make_protein_experiment_evidence_starter, make_alias_evidence_starter, \
    #     make_binding_evidence_starter, make_phosphorylation_evidence_starter
    #
    # do_conversion(make_alias_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Aliasevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(Aliasevidence), name='convert.from_bud.evidence.alias', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Aliasevidence, Evidence, 'ALIAS')
    #
    # do_conversion(make_binding_evidence_starter(nex_session_maker),
    #                [Json2Obj(Bindingevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(Bindingevidence), name='convert.from_bud.evidence.binding', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bindingevidence, Evidence, 'BINDING')
    #
    # do_conversion(make_ecnumber_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(ECNumberevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(ECNumberevidence), name='convert.from_bud.evidence.ecnumber', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, ECNumberevidence, Evidence, 'ECNUMBER')
    #
    # do_conversion(make_domain_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Domainevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(Domainevidence), name='convert.from_bud.evidence.domain', delete_untouched=True, commit_interval=1000),
    #                 OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Domainevidence, Evidence, 'DOMAIN')
    #
    # do_conversion(make_phosphorylation_evidence_starter(nex_session_maker),
    #               [Json2Obj(Phosphorylationevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Phosphorylationevidence), name='convert.from_bud.evidence.phosphorylation', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Phosphorylationevidence, Evidence, 'PHOSPHORYLATION')
    #
    # do_conversion(make_protein_experiment_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Proteinexperimentevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Proteinexperimentevidence), name='convert.from_bud.evidence.protein_experiment', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Proteinexperimentevidence, Evidence, 'PROTEINEXPERIMENT')
    #
    # from src.sgd.model.nex.evidence import Property, Bioentityproperty, Bioconceptproperty, Bioitemproperty, Chemicalproperty, Temperatureproperty, Generalproperty
    # clean_up_orphans(nex_session_maker, Bioentityproperty, Property, 'BIOENTITY')
    # clean_up_orphans(nex_session_maker, Bioconceptproperty, Property, 'BIOCONCEPT')
    # clean_up_orphans(nex_session_maker, Bioitemproperty, Property, 'BIOITEM')
    # clean_up_orphans(nex_session_maker, Chemicalproperty, Property, 'CHEMICAL')
    # clean_up_orphans(nex_session_maker, Temperatureproperty, Property, 'TEMPERATURE')
    # clean_up_orphans(nex_session_maker, Generalproperty, Property, 'CONDITION')

    # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityDetails
    from src.sgd.model.perf.bioconcept_data import BioconceptDetails
    from src.sgd.model.perf.bioitem_data import BioitemDetails

    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioitem import Domain
    from src.sgd.model.nex.bioconcept import ECNumber

    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    domain_ids = [x.id for x in nex_session.query(Domain).all()]
    ecnumber_ids = [x.id for x in nex_session.query(ECNumber).all()]
    nex_session.close()

    # do_conversion(make_locus_data_backend_starter(nex_backend, 'ec_number_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'EC_NUMBER', locus_ids, name='convert.from_backend.ec_number_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_ecnumber_data_backend_starter(nex_backend, 'ec_number_details', ecnumber_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'EC_NUMBER_LOCUS', ecnumber_ids, name='convert.from_backend.ec_number_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'protein_domain_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PROTEIN_DOMAIN', locus_ids, name='convert.from_backend.protein_domain_details', commit_interval=1000),
    #                 OutputTransformer(1000)])

    do_conversion(make_domain_data_backend_starter(nex_backend, 'protein_domain_details', domain_ids),
                   [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'PROTEIN_DOMAIN_LOCUS', domain_ids, name='convert.from_backend.protein_domain_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_locus_data_backend_starter(nex_backend, 'protein_phosphorylation_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PROTEIN_PHOSPHORYLATION', locus_ids, name='convert.from_backend.protein_phosphorylation_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_locus_data_backend_starter(nex_backend, 'protein_experiment_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PROTEIN_EXPERIMENT', locus_ids, name='convert.from_backend.protein_experiment_details', commit_interval=1000),
                    OutputTransformer(1000)])

    do_conversion(make_locus_data_backend_starter(nex_backend, 'binding_site_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'BINDING_SITE', locus_ids, name='convert.from_backend.binding_site_details', commit_interval=1000),
                    OutputTransformer(1000)])