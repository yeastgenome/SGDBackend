from src.sgd.convert import config, prepare_schema_connection, check_session_maker
from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend

__author__ = 'kpaskov'

if __name__ == "__main__":   

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    check_session_maker(bud_session_maker, 'pastry.stanford.edu:1521', config.BUD_SCHEMA)

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    check_session_maker(nex_session_maker, 'sgd-dev-db.stanford.edu:1521', config.NEX_SCHEMA)

    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    check_session_maker(perf_session_maker, 'sgd-dev-db.stanford.edu:1521', config.PERF_SCHEMA)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    bud_session = bud_session_maker()

    # # ------------------------------------------ Bioentity ------------------------------------------
    # # Bud -> Nex
    # from src.sgd.model.nex.bioentity import Locus, Transcript, Protein, Complex
    # do_conversion(make_locus_starter(bud_session),
    #               [BudObj2LocusObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Locus), name='convert.bud2nex.bioentity.locus')],
    #               delete_untouched=True, commit=True)
    #
    # do_conversion(make_complex_starter(),
    #               [BudObj2ComplexObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Complex), name='convert.bud2nex.bioentity.complex')],
    #               delete_untouched=True, commit=True)
    #
    #
    # # Nex -> Perf
    # from src.sgd.model.perf.core import Bioentity as PerfBioentity
    # do_conversion(make_backend_starter(nex_backend, 'all_bioentities', 1000),
    #               [Json2Obj(),
    #                Obj2CorePerfDB(perf_session_maker, PerfBioentity, name='convert.nex2perf.bioentity')],
    #               delete_untouched=True, commit=True)

    # # ------------------------------------------ Bioconcept ------------------------------------------
    # # Bud -> Nex
    # from src.sgd.model.nex.bioconcept import Phenotype, Go, ECNumber
    # do_conversion(make_phenotype_starter(bud_session),
    #               [BudObj2PhenotypeObj(bud_session_maker, nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Phenotype), name='convert.bud2nex.bioconcept.phenotype')],
    #               delete_untouched=True, commit=True)
    #
    # do_conversion(make_go_starter(bud_session),
    #               [BudObj2GoObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Go), name='convert.bud2nex.bioconcept.go')],
    #               delete_untouched=True, commit=True)
    #
    # do_conversion(make_ecnumber_starter(bud_session),
    #               [BudObj2ECNumberObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(ECNumber), name='convert.bud2nex.bioconcept.ecnumber')],
    #               delete_untouched=True, commit=True)
    #
    # # Nex -> Perf
    # from src.sgd.model.perf.core import Bioconcept as PerfBioconcept
    # do_conversion(make_backend_starter(nex_backend, 'all_bioconcepts', 1000),
    #               [Json2Obj(),
    #                Obj2CorePerfDB(perf_session_maker, PerfBioconcept, name='convert.nex2perf.bioconcept')],
    #               delete_untouched=True, commit=True)

    # # ------------------------------------------ Bioitem ------------------------------------------
    # # Bud -> Nex
    # from src.sgd.model.nex.bioitem import Orphanbioitem, Allele, Domain, Chemical
    # do_conversion(make_orphan_starter(bud_session),
    #               [BudObj2OrphanObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Orphanbioitem), name='convert.bud2nex.bioitem.orphan')],
    #               delete_untouched=True, commit=True)
    #
    # do_conversion(make_allele_starter(bud_session),
    #               [BudObj2AlleleObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Allele), name='convert.bud2nex.bioitem.allele')],
    #               delete_untouched=True, commit=True)
    #
    # do_conversion(make_domain_starter(bud_session),
    #               [BudObj2DomainObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Domain), name='convert.bud2nex.bioitem.domain')],
    #               delete_untouched=True, commit=True)
    #
    # do_conversion(make_chemical_starter(bud_session),
    #               [BudObj2ChemicalObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Chemical), name='convert.bud2nex.bioitem.chemical')],
    #               delete_untouched=True, commit=True)
    #
    # # Nex -> Perf
    # from src.sgd.model.perf.core import Bioitem as PerfBioitem
    # do_conversion(make_backend_starter(nex_backend, 'all_bioitems', 1000),
    #               [Json2Obj(),
    #                Obj2CorePerfDB(perf_session_maker, PerfBioitem, name='convert.nex2perf.bioitem')],
    #               delete_untouched=True, commit=True)
    #
    # bud_session.close()

    # # ------------------------------------------ Evelements ------------------------------------------
    # # Bud -> Nex
    # from src.sgd.model.nex.misc import Experiment, Strain, Source
    # do_conversion(make_experiment_starter(bud_session),
    #               [BudObj2ExperimentObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Experiment), name='convert.bud2nex.experiment')],
    #               delete_untouched=True, commit=True)

    # do_conversion(make_strain_starter(bud_session),
    #               [BudObj2StrainObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Strain), name='convert.bud2nex.strain')],
    #               delete_untouched=True, commit=True)

    # do_conversion(make_source_starter(bud_session),
    #               [BudObj2SourceObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Source), name='convert.bud2nex.source')],
    #               delete_untouched=True, commit=True)

    # # ------------------------------------------ Evidence ------------------------------------------
    # # Bud -> Nex
    # from src.sgd.model.nex.evidence import Geninteractionevidence, Physinteractionevidence
    # do_conversion(make_interaction_evidence_starter(bud_session, 'genetic interactions'),
    #               [BudObj2InteractionEvidenceObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Geninteractionevidence), name='convert.bud2nex.evidence.geninteraction'),
    #                OutputTransformer(1000)],
    #               delete_untouched=True, commit=False)
    #
    # do_conversion(make_interaction_evidence_starter(bud_session, 'physical interactions'),
    #               [BudObj2InteractionEvidenceObj(nex_session_maker),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Physinteractionevidence), name='convert.bud2nex.evidence.physinteraction'),
    #                OutputTransformer(1000)],
    #               delete_untouched=True, commit=False)
    #
    # bud_session.close()

    from src.sgd.convert.bud2nex.evidence.phosphorylation import convert
    convert(nex_session_maker)