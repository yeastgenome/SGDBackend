from src.sgd.model import bud, nex
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Json2Obj, Evidence2NexDB

__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    from src.sgd.model.nex.evidence import Evidence, Goevidence, Literatureevidence, Domainevidence, ECNumberevidence, \
        Proteinexperimentevidence, Phenotypeevidence, Historyevidence, Pathwayevidence, Goslimevidence, Posttranslationalevidence
    from src.sgd.convert.from_bud.evidence import make_go_evidence_starter, make_literature_evidence_starter, \
        make_domain_evidence_starter, make_protein_experiment_evidence_starter, \
        make_ecnumber_evidence_starter, make_protein_experiment_evidence_starter, make_go_slim_evidence_starter, \
        make_phenotype_evidence_starter, make_history_evidence_starter, make_pathway_evidence_starter, make_posttranslational_evidence_starter
    from src.sgd.convert.from_bud.auxiliary import make_bioconcept_count_starter

    do_conversion(make_go_evidence_starter(bud_session_maker, nex_session_maker),
                   [Json2Obj(Goevidence),
                    Evidence2NexDB(nex_session_maker, lambda x: x.query(Goevidence),
                                   name='convert.from_bud.evidence.go',
                                   delete_untouched=True,
                                   commit_interval=1000,
                                   already_deleted=clean_up_orphans(nex_session_maker, Goevidence, Evidence, 'GO'))])

    do_conversion(make_go_slim_evidence_starter(nex_session_maker),
                   [Json2Obj(Goslimevidence),
                    Evidence2NexDB(nex_session_maker, lambda x: x.query(Goslimevidence),
                                   name='convert.from_bud.evidence.goslim',
                                   delete_untouched=True,
                                   commit_interval=1000,
                                   already_deleted=clean_up_orphans(nex_session_maker, Goslimevidence, Evidence, 'GOSLIM'))])

    do_conversion(make_literature_evidence_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Literatureevidence),
                   Evidence2NexDB(nex_session_maker, lambda x: x.query(Literatureevidence),
                                  name='convert.from_bud.evidence.literature',
                                  delete_untouched=True,
                                  commit_interval=1000,
                                  already_deleted=clean_up_orphans(nex_session_maker, Literatureevidence, Evidence, 'LITERATURE'))])

    # do_conversion(make_binding_evidence_starter(nex_session_maker),
    #                [Json2Obj(Bindingevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(Bindingevidence),
    #                                name='convert.from_bud.evidence.binding',
    #                                delete_untouched=True,
    #                                commit=True,
    #                                already_deleted=clean_up_orphans(nex_session_maker, Bindingevidence, Evidence, 'BINDING'))])

    do_conversion(make_ecnumber_evidence_starter(bud_session_maker, nex_session_maker),
                   [Json2Obj(ECNumberevidence),
                    Evidence2NexDB(nex_session_maker, lambda x: x.query(ECNumberevidence),
                                   name='convert.from_bud.evidence.ecnumber',
                                   delete_untouched=True,
                                   commit=True,
                                   already_deleted=clean_up_orphans(nex_session_maker, ECNumberevidence, Evidence, 'ECNUMBER'))])

    do_conversion(make_domain_evidence_starter(bud_session_maker, nex_session_maker),
                   [Json2Obj(Domainevidence),
                    Evidence2NexDB(nex_session_maker, lambda x: x.query(Domainevidence),
                                   name='convert.from_bud.evidence.domain',
                                   delete_untouched=True,
                                   commit_interval=1000,
                                   already_deleted=clean_up_orphans(nex_session_maker, Domainevidence, Evidence, 'DOMAIN'))])

    # do_conversion(make_phosphorylation_evidence_starter(nex_session_maker),
    #               [Json2Obj(Phosphorylationevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Phosphorylationevidence),
    #                               name='convert.from_bud.evidence.phosphorylation',
    #                               delete_untouched=True,
    #                               commit=True,
    #                               already_deleted=clean_up_orphans(nex_session_maker, Phosphorylationevidence, Evidence, 'PHOSPHORYLATION'))])

    do_conversion(make_protein_experiment_evidence_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Proteinexperimentevidence),
                   Evidence2NexDB(nex_session_maker, lambda x: x.query(Proteinexperimentevidence),
                                  name='convert.from_bud.evidence.protein_experiment',
                                  delete_untouched=True,
                                  commit=True,
                                  already_deleted=clean_up_orphans(nex_session_maker, Proteinexperimentevidence, Evidence, 'PROTEINEXPERIMENT'))])

    do_conversion(make_phenotype_evidence_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Phenotypeevidence),
                   Evidence2NexDB(nex_session_maker, lambda x: x.query(Phenotypeevidence),
                                  name='convert.from_bud.evidence.phenotype',
                                  delete_untouched=True,
                                  commit_interval=1000,
                                  already_deleted=clean_up_orphans(nex_session_maker, Phenotypeevidence, Evidence, 'PHENOTYPE'))])

    make_bioconcept_count_starter(nex_session_maker)

    do_conversion(make_history_evidence_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Historyevidence),
                   Evidence2NexDB(nex_session_maker, lambda x: x.query(Historyevidence),
                                  name='convert.from_bud.evidence.history',
                                  delete_untouched=True,
                                  commit_interval=1000,
                                  already_deleted=clean_up_orphans(nex_session_maker, Historyevidence, Evidence, 'HISTORY'))])

    do_conversion(make_pathway_evidence_starter(bud_session_maker, nex_session_maker),
                   [Json2Obj(Pathwayevidence),
                    Evidence2NexDB(nex_session_maker, lambda x: x.query(Pathwayevidence),
                                   name='convert.from_bud.evidence.pathway',
                                   delete_untouched=True,
                                   commit_interval=1000,
                                   already_deleted=clean_up_orphans(nex_session_maker, Pathwayevidence, Evidence, 'PATHWAY'))])

    # do_conversion(make_posttranslational_evidence_starter(nex_session_maker),
    #               [Json2Obj(Posttranslationalevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Posttranslationalevidence),
    #                               name='convert.from_bud.evidence.posttranslationsl',
    #                               delete_untouched=True,
    #                               commit_interval=1000,
    #                               already_deleted=clean_up_orphans(nex_session_maker, Posttranslationalevidence, Evidence, 'POSTTRANSLATIONAL'))])

