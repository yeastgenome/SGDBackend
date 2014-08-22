from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, OutputTransformer, make_file_starter, \
    make_backend_starter, Json2CorePerfDB, make_individual_locus_backend_starter, Json2DataPerfDB, make_individual_complex_backend_starter, \
    make_individual_go_backend_starter, make_individual_phenotype_backend_starter, make_individual_observable_backend_starter, Evidence2NexDB, make_locus_data_backend_starter, \
    make_reference_data_backend_starter, make_ecnumber_data_backend_starter, make_go_data_backend_starter, make_phenotype_data_backend_starter, make_observable_data_backend_starter, \
    make_chemical_data_backend_starter, make_observable_data_backend_starter, make_contig_data_backend_starter, make_domain_data_backend_starter, \
    BigObj2NexDB, Json2DisambigPerfDB, make_orphan_backend_starter, Json2OrphanPerfDB, make_go_data_with_children_backend_starter, make_datasetcolumn_data_backend_starter, make_orphan_arg_backend_starter
from sqlalchemy.orm import with_polymorphic
import os
__author__ = 'kpaskov'

if __name__ == "__main__":   

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # # ------------------------------------------ Evelements ------------------------------------------
    # # Bud -> Nex
    from src.sgd.model.nex.misc import Source, Strain, Experiment, Experimentalias, Experimentrelation, Url, Alias, Relation, Strainurl
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.convert.from_bud.evelements import make_source_starter, make_strain_starter, make_experiment_starter, \
        make_experiment_alias_starter, make_experiment_relation_starter, make_strain_url_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter

    # do_conversion(make_source_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Source),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Source), name='convert.from_bud.source', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_experiment_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Experiment),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Experiment), name='convert.from_bud.experiment', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_strain_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Strain),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Strain), name='convert.from_bud.strain', delete_untouched=True, commit=True)])

    # do_conversion(make_strain_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Strain),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Strain), name='convert.from_bud.strain', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_strain_url_starter(nex_session_maker),
    #               [Json2Obj(Strainurl),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Strainurl), name='convert.from_bud.strain.url', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(10000)])
    # clean_up_orphans(nex_session_maker, Strainurl, Url, 'STRAIN')
    #
    # do_conversion(make_experiment_alias_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Experimentalias),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Experimentalias), name='convert.from_bud.experiment_alias', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Experimentalias, Alias, 'EXPERIMENT')
    #
    # do_conversion(make_experiment_relation_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Experimentrelation),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Experimentrelation), name='convert.from_bud.experiment_relation', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Experimentrelation, Relation, 'EXPERIMENT')
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Strain, ['id', 'format_name'], 'STRAIN', None),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'STRAIN'), name='convert.from_bud.strain.disambig', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Experiment, ['id', 'eco_id', 'format_name'], 'EXPERIMENT', None),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'EXPERIMENT'), name='convert.from_bud.experiment.disambig', delete_untouched=True, commit=True)])

    # # Nex -> Perf
    # from src.sgd.model.perf.core import Strain as PerfStrain, Experiment as PerfExperiment
    # do_conversion(make_backend_starter(nex_backend, 'all_strains', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfStrain, name='convert.from_backend.strain', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])
    #
    # do_conversion(make_backend_starter(nex_backend, 'all_experiments', 100),
    #               [Json2CorePerfDB(perf_session_maker, PerfExperiment, name='convert.from_backend.experiment', commit_interval=100, delete_untouched=True),
    #                OutputTransformer(100)])

    # # ------------------------------------------ Bioentity ------------------------------------------
    # # Bud -> Nex

    from src.sgd.model.nex.bioentity import Bioentity, Locus, Complex, Bioentityalias, Bioentityrelation, Bioentityurl
    from src.sgd.model.nex.misc import Alias, Relation, Url
    from src.sgd.model.nex.auxiliary import Locustabs, Disambig
    from src.sgd.convert.from_bud.bioentity import make_locus_starter, make_complex_starter, make_bioentity_tab_starter, \
        make_bioentity_alias_starter, make_bioentity_relation_starter, make_bioentity_url_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
    #
    # do_conversion(make_locus_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Locus),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Locus), name='convert.from_bud.bioentity.locus', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Locus, Bioentity, 'LOCUS')
    #
    # do_conversion(make_complex_starter(nex_session_maker),
    #               [Json2Obj(Complex),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Complex), name='convert.from_bud.bioentity.complex', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Locus, Bioentity, 'LOCUS')
    #
    # do_conversion(make_bioentity_tab_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Locustabs),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Locustabs), name='convert.from_bud.bioentity.locustabs', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_bioentity_alias_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioentityalias),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityalias), name='convert.from_bud.bioentity.alias', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bioentityalias, Alias, 'BIOENTITY')
    #
    # do_conversion(make_bioentity_relation_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioentityrelation),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityrelation), name='convert.from_bud.bioentity.relation', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bioentityrelation, Relation, 'BIOENTITY')
    #
    # do_conversion(make_bioentity_url_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioentityurl),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityurl), name='convert.from_bud.bioentity.url', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(10000)])
    # clean_up_orphans(nex_session_maker, Bioentityurl, Url, 'BIOENTITY')
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Locus, ['id', 'format_name', 'display_name', 'sgdid'], 'BIOENTITY', 'LOCUS'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOENTITY').filter(Disambig.subclass_type == 'LOCUS'), name='convert.from_bud.bioentity.disambig.locus', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Complex, ['id', 'format_name'], 'BIOENTITY', 'COMPLEX'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOENTITY').filter(Disambig.subclass_type == 'COMPLEX'), name='convert.from_bud.bioentity.disambig.complex', delete_untouched=True, commit=True)])

    # # Nex -> Perf
    # from src.sgd.model.perf.core import Bioentity as PerfBioentity, Locustab as PerfLocustab, Locusentry as PerfLocusentry
    # do_conversion(make_backend_starter(nex_backend, 'all_bioentities', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioentity, name='convert.from_backend.bioentity', commit_interval=10, delete_untouched=True),
    #                OutputTransformer(10)])
    #
    # do_conversion(make_backend_starter(nex_backend, 'all_locustabs', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfLocustab, name='convert.from_backend.all_locustabs', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])
    #
    # do_conversion(make_backend_starter(nex_backend, 'all_locusentries', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfLocusentry, name='convert.from_backend.all_locusentries', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])

    # ------------------------------------------ Bioconcept ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.bioconcept import Bioconcept, Observable, Phenotype, Go, ECNumber, Bioconceptalias, Bioconceptrelation, Bioconcepturl
    from src.sgd.model.nex.misc import Alias, Relation, Url
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.convert.from_bud.bioconcept import make_phenotype_starter, make_go_starter, \
        make_ecnumber_starter, make_bioconcept_alias_starter, make_bioconcept_relation_starter, make_observable_starter, make_bioconcept_url_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
    #
    # do_conversion(make_observable_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Observable),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Observable), name='convert.from_bud.bioconcept.observable', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Observable, Bioconcept, 'OBSERVABLE')
    #
    # do_conversion(make_phenotype_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Phenotype),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Phenotype), name='convert.from_bud.bioconcept.phenotype', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Phenotype, Bioconcept, 'PHENOTYPE')
    #
    # do_conversion(make_go_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Go),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Go), name='convert.from_bud.bioconcept.go', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Go, Bioconcept, 'GO')
    #
    # do_conversion(make_ecnumber_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(ECNumber),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(ECNumber), name='convert.from_bud.bioconcept.ecnumber', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, ECNumber, Bioconcept, 'EC_NUMBER')
    #
    # do_conversion(make_bioconcept_relation_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioconceptrelation),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconceptrelation), name='convert.from_bud.bioconcept.relation', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(10000)])
    # clean_up_orphans(nex_session_maker, Bioconceptrelation, Relation, 'BIOCONCEPT')
    #
    # do_conversion(make_bioconcept_alias_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioconceptalias),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconceptalias), name='convert.from_bud.bioconcept.alias', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Bioconceptalias, Alias, 'BIOCONCEPT')
    #
    # do_conversion(make_bioconcept_url_starter(nex_session_maker),
    #               [Json2Obj(Bioconcepturl),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconcepturl), name='convert.from_bud.bioconcept.url', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Bioconcepturl, Url, 'BIOCONCEPT')
    #
    # do_conversion(make_disambig_starter(nex_session_maker, ECNumber, ['id', 'format_name'], 'BIOCONCEPT', 'ECNUMBER'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'ECNUMBER'), name='convert.from_bud.bioconcept.disambig.ecnumber', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Observable, ['id', 'format_name'], 'BIOCONCEPT', 'OBSERVABLE'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'OBSERVABLE'), name='convert.from_bud.bioconcept.disambig.observable', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Phenotype, ['id', 'format_name'], 'BIOCONCEPT', 'PHENOTYPE'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'PHENOTYPE'), name='convert.from_bud.bioconcept.disambig.phenotype', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Go, ['id', 'format_name'], 'BIOCONCEPT', 'GO'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'GO'), name='convert.from_bud.bioconcept.disambig.go', delete_untouched=True, commit=True)])

    # # Nex -> Perf
    # from src.sgd.model.perf.core import Bioconcept as PerfBioconcept
    # do_conversion(make_backend_starter(nex_backend, 'all_bioconcepts', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioconcept, name='convert.from_backend.bioconcept', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])

    # ------------------------------------------ Bioitem ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.bioitem import Bioitem, Orphanbioitem, Domain, Allele, Chemical, Bioitemurl, Bioitemrelation, \
        Bioitemalias, Contig, Dataset, Datasetcolumn, BioitemTag
    from src.sgd.model.nex.misc import Alias, Relation, Url, Tag
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.convert.from_bud.bioitem import make_allele_starter, make_chemical_starter, make_domain_starter, \
        make_orphan_starter, make_contig_starter, make_bioitem_url_starter, make_bioitem_relation_starter, make_dataset_starter, make_datasetcolumn_starter, make_bioitem_tag_starter, make_tag_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
    #
    # do_conversion(make_orphan_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Orphanbioitem),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Orphanbioitem), name='convert.from_bud.bioitem.orphan', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Orphanbioitem, Bioitem, 'ORPHAN')
    #
    # do_conversion(make_allele_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Allele),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Allele), name='convert.from_bud.bioitem.allele', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Allele, Bioitem, 'ALLELE')
    #
    # do_conversion(make_domain_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Domain),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Domain), name='convert.from_bud.bioitem.domain', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Domain, Bioitem, 'DOMAIN')
    #
    # do_conversion(make_chemical_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Chemical),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Chemical), name='convert.from_bud.bioitem.chemical', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Chemical, Bioitem, 'CHEMICAL')
    #
    # do_conversion(make_contig_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Contig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Contig), name='convert.from_bud.bioitem.contig', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Contig, Bioitem, 'CONTIG')
    # #
    # do_conversion(make_dataset_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14'),
    #               [Json2Obj(Dataset),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Dataset), name='convert.from_bud.bioitem.dataset', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Dataset, Bioitem, 'DATASET')
    #
    # do_conversion(make_datasetcolumn_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14'),
    #               [Json2Obj(Datasetcolumn),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Datasetcolumn), name='convert.from_bud.bioitem.datasetcolumn', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Datasetcolumn, Bioitem, 'DATASETCOLUMN')
    #
    # do_conversion(make_bioitem_relation_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioitemrelation),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemrelation), name='convert.from_bud.bioitem.relation', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bioitemrelation, Relation, 'BIOITEM')
    #
    # do_conversion(make_bioitem_url_starter(nex_session_maker),
    #               [Json2Obj(Bioitemurl),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemurl), name='convert.from_bud.bioitem.url', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bioitemurl, Url, 'BIOITEM')
    #
    # do_conversion(make_tag_starter(nex_session_maker),
    #               [Json2Obj(Tag),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Tag), name='convert.from_bud.tag', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Tag, ['id', 'format_name'], 'TAG', None),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'TAG'), name='convert.from_bud.bioitem.disambig.tag', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_bioitem_tag_starter(nex_session_maker),
    #               [Json2Obj(BioitemTag),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(BioitemTag), name='convert.from_bud.bioitem.tag', delete_untouched=True, commit=True)])

    # do_conversion(make_disambig_starter(nex_session_maker, Domain, ['id', 'format_name'], 'BIOITEM', 'DOMAIN'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'DOMAIN'), name='convert.from_bud.bioitem.disambig.domain', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Chemical, ['id', 'format_name'], 'BIOITEM', 'CHEMICAL'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'CHEMICAL'), name='convert.from_bud.bioitem.disambig.chemical', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Contig, ['id', 'format_name'], 'BIOITEM', 'CONTIG'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'CONTIG'), name='convert.from_bud.bioitem.disambig.contig', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Dataset, ['id', 'format_name'], 'BIOITEM', 'DATASET'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'DATASET'), name='convert.from_bud.bioitem.disambig.dataset', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Datasetcolumn, ['id', 'format_name'], 'BIOITEM', 'DATASETCOLUMN'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'DATASETCOLUMN'), name='convert.from_bud.bioitem.disambig.datasetcolumn', delete_untouched=True, commit=True)])

    # Nex -> Perf
    from src.sgd.model.perf.core import Bioitem as PerfBioitem, Tag as PerfTag
    # do_conversion(make_backend_starter(nex_backend, 'all_bioitems', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioitem, name='convert.from_backend.bioitem', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])
    # do_conversion(make_backend_starter(nex_backend, 'all_tags', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfTag, name='convert.from_backend.tag', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])

    # ------------------------------------------ Reference ------------------------------------------
    # Bud -> Nex
    # from src.sgd.model.nex.reference import Reference, Journal, Book, Author, Referencealias, Referenceurl, \
    #     Referencerelation, Bibentry, AuthorReference, ReferenceReftype, Reftype
    # from src.sgd.model.nex.misc import Alias, Relation, Url
    # from src.sgd.model.nex.auxiliary import Disambig
    # from src.sgd.convert.from_bud.reference import make_reference_starter, make_journal_starter, make_book_starter,\
    #     make_bibentry_starter, make_reftype_starter, make_reference_alias_starter, \
    #     make_author_reference_starter, make_author_starter, make_ref_reftype_starter, make_reference_relation_starter, \
    #     make_reference_url_starter
    # from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
    #
    # do_conversion(make_journal_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Journal),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Journal), name='convert.from_bud.journal', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_book_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Book),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Book), name='convert.from_bud.book', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_reference_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Reference),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Reference), name='convert.from_bud.reference', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    #
    # do_conversion(make_bibentry_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bibentry),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bibentry), name='convert.from_bud.bibentry', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    #
    # do_conversion(make_author_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Author),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Author), name='convert.from_bud.author', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_author_reference_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(AuthorReference),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(AuthorReference), name='convert.from_bud.author_reference', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_reftype_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Reftype),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Reftype), name='convert.from_bud.reftype', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_ref_reftype_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(ReferenceReftype),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(ReferenceReftype), name='convert.from_bud.reference_reftype', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_reference_relation_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Referencerelation),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Referencerelation), name='convert.from_bud.reference_relation', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Referencerelation, Relation, 'REFERENCE')
    #
    # do_conversion(make_reference_alias_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Referencealias),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Referencealias), name='convert.from_bud.reference_alias', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Referencealias, Alias, 'REFERENCE')
    #
    # do_conversion(make_reference_url_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Referenceurl),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Referenceurl), name='convert.from_bud.reference_url', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Referenceurl, Url, 'REFERENCE')
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Reference, ['id', 'sgdid', 'pubmed_id', 'doi'], 'REFERENCE', None),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'REFERENCE'), name='convert.from_bud.reference.disambig', delete_untouched=True, commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Author, ['format_name', 'id'], 'AUTHOR', None),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'AUTHOR'), name='convert.from_bud.author.disambig', delete_untouched=True, commit=True)])

    # # Nex -> Perf
    # from src.sgd.model.perf.core import Reference as PerfReference, Author as PerfAuthor, Bibentry as PerfBibentry
    # do_conversion(make_backend_starter(nex_backend, 'all_references', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfReference, name='convert.from_backend.reference', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    #
    # do_conversion(make_backend_starter(nex_backend, 'all_authors', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfAuthor, name='convert.from_backend.author', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])

    # do_conversion(make_backend_starter(nex_backend, 'all_bibentries', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBibentry, name='convert.from_backend.all_bibentries', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])
    # ------------------------------------------ Evidence ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.evidence import Evidence, Goevidence, DNAsequenceevidence, Regulationevidence, \
        Proteinsequenceevidence, Phosphorylationevidence, Domainevidence, Literatureevidence, Phenotypeevidence, \
        DNAsequencetag, Expressionevidence, Bioentitydata, Aliasevidence, Bindingevidence, Bioentityevidence, \
        Complexevidence, ECNumberevidence, Geninteractionevidence, Physinteractionevidence, Proteinexperimentevidence, Historyevidence
    from src.sgd.model.nex.archive import ArchiveLiteratureevidence
    from src.sgd.convert.from_bud.evidence import make_go_evidence_starter, make_dna_sequence_evidence_starter, \
        make_regulation_evidence_starter, make_protein_sequence_evidence_starter, make_phosphorylation_evidence_starter, \
        make_domain_evidence_starter, make_literature_evidence_starter, make_phenotype_evidence_starter, \
        make_dna_sequence_tag_starter, make_expression_evidence_starter, make_expression_data_starter, \
        make_alias_evidence_starter, make_binding_evidence_starter, make_bioentity_evidence_starter, \
        make_complex_evidence_starter, make_ecnumber_evidence_starter, make_interaction_evidence_starter, \
        make_archive_literature_evidence_starter, make_protein_experiment_evidence_starter, make_history_evidence_starter, make_new_dna_sequence_evidence_starter

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
    # do_conversion(make_complex_evidence_starter(nex_session_maker),
    #                [Json2Obj(Complexevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(Complexevidence), name='convert.from_bud.evidence.complex', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Complexevidence, Evidence, 'COMPLEX')
    #
    # do_conversion(make_domain_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Domainevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(Domainevidence), name='convert.from_bud.evidence.domain', delete_untouched=True, commit_interval=1000),
    #                 OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Domainevidence, Evidence, 'DOMAIN')
    #
    # do_conversion(make_ecnumber_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(ECNumberevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(ECNumberevidence), name='convert.from_bud.evidence.ecnumber', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, ECNumberevidence, Evidence, 'ECNUMBER')
    #
    # do_conversion(make_go_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Goevidence),
    #                 Evidence2NexDB(nex_session_maker, lambda x: x.query(Goevidence), name='convert.from_bud.evidence.go', delete_untouched=True, commit_interval=1000),
    #                 OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Goevidence, Evidence, 'GO')
    #
    # do_conversion(make_interaction_evidence_starter(bud_session_maker, nex_session_maker, 'genetic interactions'),
    #               [Json2Obj(Geninteractionevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Geninteractionevidence), name='convert.from_bud.evidence.geninteraction', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Geninteractionevidence, Evidence, 'GENINTERACTION')
    #
    # do_conversion(make_interaction_evidence_starter(bud_session_maker, nex_session_maker, 'physical interactions'),
    #               [Json2Obj(Physinteractionevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Physinteractionevidence), name='convert.from_bud.evidence.physinteraction', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Physinteractionevidence, Evidence, 'PHYSINTERACTION')
    #
    # do_conversion(make_literature_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Literatureevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Literatureevidence), name='convert.from_bud.evidence.literature', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Literatureevidence, Evidence, 'LITERATURE')
    #
    # do_conversion(make_archive_literature_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(ArchiveLiteratureevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(ArchiveLiteratureevidence), name='convert.from_bud.evidence.archive_literature', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, ArchiveLiteratureevidence, Evidence, 'ARCH_LITERATURE')
    #
    # do_conversion(make_phenotype_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Phenotypeevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Phenotypeevidence), name='convert.from_bud.evidence.phenotype', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Phenotypeevidence, Evidence, 'PHENOTYPE')
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
    # do_conversion(make_regulation_evidence_starter(nex_session_maker),
    #               [Json2Obj(Regulationevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Regulationevidence), name='convert.from_bud.evidence.regulation', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Regulationevidence, Evidence, 'REGULATION')


    # do_conversion(make_ref_dna_sequence_evidence_starter(bud_session_maker, nex_session_maker, ["src/sgd/convert/data/strains/orf_coding_all.fasta", "src/sgd/convert/data/strains/rna_coding.fasta"]),
    #                   [Json2Obj(DNAsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.strain_id == 1), name='convert.from_bud.evidence.reference_dnasequence', delete_untouched=True, commit_interval=1000),
    #                    OutputTransformer(1000)])
    #
    # do_conversion(make_dna_sequence_tag_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(DNAsequencetag),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequencetag), name='convert.from_bud.evidence.dnasequence.tags', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    #
    # from src.sgd.convert.from_bud import sequence_files, protein_sequence_files, new_sequence_files
    # from src.sgd.model.nex.misc import Strain
    # nex_session = nex_session_maker()
    # strain_key_to_id = dict([(x.unique_key(), x.id) for x in nex_session.query(Strain).all()])
    # nex_session.close()

    # for sequence_filename, coding_sequence_filename, strain_key in sequence_files:
    #     do_conversion(make_dna_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, coding_sequence_filename),
    #                   [Json2Obj(DNAsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.strain_id == strain_key_to_id[strain_key]), name='convert.from_bud.evidence.dnasequence', delete_untouched=True, commit_interval=1000),
    #                    OutputTransformer(1000)])
    #
    # for sequence_filename, strain_key in new_sequence_files:
    #     do_conversion(make_new_dna_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename),
    #                   [Json2Obj(DNAsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.strain_id == strain_key_to_id[strain_key]), name='convert.from_bud.evidence.dnasequence', delete_untouched=True, commit_interval=1000),
    #                    OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, DNAsequenceevidence, Evidence, 'DNASEQUENCE')
    #
    #
    # protparam_data = dict([(row[0], row) for row in make_file_starter('src/sgd/convert/data/ProtParam.txt')()])
    # for sequence_filename, strain_key in protein_sequence_files:
    #     do_conversion(make_protein_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, protparam_data),
    #                   [Json2Obj(Proteinsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(Proteinsequenceevidence).filter(Proteinsequenceevidence.strain_id == strain_key_to_id[strain_key]), name='convert.from_bud.evidence.proteinsequence', delete_untouched=True, commit_interval=1000),
    #                    OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Proteinsequenceevidence, Evidence, 'PROTEINSEQUENCE')
    #
    # from src.sgd.model.nex.paragraph import Referenceparagraph
    # do_conversion(make_expression_evidence_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14'),
    #               [Json2Obj(Expressionevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Expressionevidence), name='convert.from_bud.evidence.expression', delete_untouched=False, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Expressionevidence, Evidence, 'EXPRESSION')
    #
    # from src.sgd.model.nex.bioitem import Dataset
    # from src.sgd.convert.from_bud.evidence import get_alias_info
    # nex_session = nex_session_maker()
    # dataset_key_to_id = dict([(x.unique_key(), x.id) for x in nex_session.query(Dataset).all()])
    # dataset_key_to_channel_count = dict([(x.unique_key(), x.channel_count) for x in nex_session.query(Dataset).all()])
    #
    # from src.sgd.model.nex.bioentity import Locus, Bioentityalias
    # locuses = nex_session.query(Locus).all()
    # key_to_locus = dict([(x.format_name, x) for x in locuses])
    # key_to_locus.update([(x.display_name, x) for x in locuses])
    # key_to_locus.update([('SGD:' + x.sgdid, x) for x in locuses])
    # aliases = dict()
    # for alias in nex_session.query(Bioentityalias).all():
    #     if alias.display_name in aliases:
    #         aliases[alias.display_name].add(alias.bioentity)
    #     else:
    #         aliases[alias.display_name] = set([alias.bioentity])
    # for key, locus in key_to_locus.iteritems():
    #     if key in aliases:
    #         aliases[key].add(locus)
    #
    # nex_session.close()
    # for path in os.listdir('src/sgd/convert/data/microarray_05_14'):
    #     if os.path.isdir('src/sgd/convert/data/microarray_05_14/' + path):
    #         for file in os.listdir('src/sgd/convert/data/microarray_05_14/' + path):
    #             #if file != 'README':
    #             #    get_alias_info('src/sgd/convert/data/microarray_05_14/' + path + '/' + file, key_to_locus, aliases)
    #             dataset_key = (file[:-4], 'DATASET')
    #             print dataset_key
    #             if dataset_key in dataset_key_to_id:
    #                 do_conversion(make_expression_data_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14/' + path + '/' + file, dataset_key_to_id[dataset_key], dataset_key_to_channel_count[dataset_key], key_to_locus, aliases),
    #                                   [Json2Obj(Bioentitydata),
    #                                    Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentitydata).filter(Bioentitydata.evidence.has(dataset_id=dataset_key_to_id[dataset_key])), name='convert.from_bud.evidence.expression_data', delete_untouched=True, commit_interval=1000),
    #                                    OutputTransformer(1000)])
    #
    # do_conversion(make_history_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Historyevidence),
    #                Evidence2NexDB(nex_session_maker, lambda x: x.query(Historyevidence), name='convert.from_bud.evidence.history', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Historyevidence, Evidence, 'HISTORY')

    # from src.sgd.model.nex.evidence import Property, Bioentityproperty, Bioconceptproperty, Bioitemproperty, Chemicalproperty, Temperatureproperty, Generalproperty
    # clean_up_orphans(nex_session_maker, Bioentityproperty, Property, 'BIOENTITY')
    # clean_up_orphans(nex_session_maker, Bioconceptproperty, Property, 'BIOCONCEPT')
    # clean_up_orphans(nex_session_maker, Bioitemproperty, Property, 'BIOITEM')
    # clean_up_orphans(nex_session_maker, Chemicalproperty, Property, 'CHEMICAL')
    # clean_up_orphans(nex_session_maker, Temperatureproperty, Property, 'TEMPERATURE')
    # clean_up_orphans(nex_session_maker, Generalproperty, Property, 'CONDITION')

    # # ------------------------------------------ Paragraph ------------------------------------------
    from src.sgd.model.nex.paragraph import Paragraph, ParagraphReference, Bioentityparagraph, Strainparagraph, Referenceparagraph
    from src.sgd.model.nex.misc import Source
    from src.sgd.convert.from_bud.paragraph import make_paragraph_reference_starter, make_bioentity_paragraph_starter, \
        make_strain_paragraph_starter, make_reference_paragraph_starter
    #
    # do_conversion(make_bioentity_paragraph_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioentityparagraph),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityparagraph), name='convert.from_bud.paragraph.bioentity', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Bioentityparagraph, Paragraph, 'BIOENTITY')
    #
    # do_conversion(make_strain_paragraph_starter(nex_session_maker),
    #               [Json2Obj(Strainparagraph),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Strainparagraph), name='convert.from_bud.paragraph.strain', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Strainparagraph, Paragraph, 'STRAIN')
    #
    # do_conversion(make_reference_paragraph_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Referenceparagraph),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Referenceparagraph), name='convert.from_bud.paragraph.reference', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Referenceparagraph, Paragraph, 'REFERENCE')
    #
    # do_conversion(make_paragraph_reference_starter(nex_session_maker),
    #               [Json2Obj(ParagraphReference),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(ParagraphReference), name='convert.from_bud.paragraph_reference', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])

    # ------------------------------------------ Auxilliary ------------------------------------------
    from src.sgd.model.nex.auxiliary import Interaction, Bioentityinteraction, Bioconceptinteraction, Referenceinteraction, Bioiteminteraction
    from src.sgd.convert.from_bud.auxiliary import make_bioconcept_interaction_starter, make_reference_interaction_starter, \
        make_bioitem_interaction_starter, make_bioentity_physinteraction_starter, make_bioentity_geninteraction_starter, make_bioentity_expression_interaction_starter
    #
    # do_conversion(make_bioentity_physinteraction_starter(nex_session_maker),
    #               [Json2Obj(Bioentityinteraction),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityinteraction).filter_by(interaction_type='GENINTERACTION'), name='convert.from_bud.auxilliary.bioentity_interaction_genetic', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    #
    # do_conversion(make_bioentity_geninteraction_starter(nex_session_maker),
    #               [Json2Obj(Bioentityinteraction),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityinteraction).filter_by(interaction_type='PHYSINTERACTION'), name='convert.from_bud.auxilliary.bioentity_interaction_physical', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])

    # do_conversion(make_bioentity_regulation_interaction_starter(nex_session_maker),
    #               [Json2Obj(Bioentityinteraction),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityinteraction).filter_by(interaction_type='REGULATION'), name='convert.from_bud.auxilliary.bioentity_interaction', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    #
    # do_conversion(make_bioentity_expression_interaction_starter(nex_session_maker),
    #               [Json2Obj(Bioentityinteraction),
    #                BigObj2NexDB(nex_session_maker, lambda x: x.query(Bioentityinteraction).filter_by(interaction_type='EXPRESSION'), name='convert.from_bud.auxilliary.bioentity_interaction_expression', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])

    # clean_up_orphans(nex_session_maker, Bioentityinteraction, Interaction, 'BIOENTITY')
    #
    # do_conversion(make_bioconcept_interaction_starter(nex_session_maker),
    #               [Json2Obj(Bioconceptinteraction),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconceptinteraction), name='convert.from_bud.auxilliary.bioconcept_interaction', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Bioconceptinteraction, Interaction, 'BIOCONCEPT')
    #
    # do_conversion(make_reference_interaction_starter(nex_session_maker),
    #               [Json2Obj(Referenceinteraction),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Referenceinteraction), name='convert.from_bud.auxilliary.reference_interaction', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Referenceinteraction, Interaction, 'REFERENCE')
    #
    # do_conversion(make_bioitem_interaction_starter(nex_session_maker),
    #               [Json2Obj(Bioiteminteraction),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioiteminteraction), name='convert.from_bud.auxilliary.bioitem_interaction', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Bioiteminteraction, Interaction, 'BIOITEM')

    # # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityDetails, BioentityGraph, BioentityEnrichment
    from src.sgd.model.perf.bioconcept_data import BioconceptDetails, BioconceptGraph
    from src.sgd.model.perf.bioitem_data import BioitemDetails
    from src.sgd.model.perf.reference_data import ReferenceDetails
    # do_conversion(make_backend_starter(nex_backend, 'all_disambigs', 1000),
    #                [Json2DisambigPerfDB(perf_session_maker, commit_interval=100),
    #                 OutputTransformer(1000)])

    from src.sgd.model.nex.bioentity import Locus, Complex
    from src.sgd.model.nex.bioconcept import Go, Observable, Phenotype, ECNumber
    from src.sgd.model.nex.bioitem import Chemical, Contig, Domain, Datasetcolumn
    from src.sgd.model.nex.reference import Reference
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    #ecnumber_ids = [x.id for x in nex_session.query(ECNumber).all()]
    #complex_ids = [x.id for x in nex_session.query(Complex).all()]
    #go_ids = [x.id for x in nex_session.query(Go).all()]
    #datasetcolumn_ids = [x.id for x in nex_session.query(Datasetcolumn).all()]
    #domain_ids = [x.id for x in nex_session.query(Domain).all()]
    #observable_ids = [x.id for x in nex_session.query(Observable).all()]
    #phenotype_ids = [x.id for x in nex_session.query(Phenotype).all()]
    #chemical_ids = [x.id for x in nex_session.query(Chemical).all()]
    #contig_ids = [x.id for x in nex_session.query(Contig).all()]
    #reference_ids = [x.id for x in nex_session.query(Reference).all()]
    nex_session.close()

    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'neighbor_sequence_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'NEIGHBOR_SEQUENCE', locus_ids, name='convert.from_backend.neighbor_sequence_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'sequence_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'SEQUENCE', locus_ids, name='convert.from_backend.sequence_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_contig_data_backend_starter(nex_backend, 'sequence_details', contig_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'SEQUENCE', contig_ids, name='convert.from_backend.sequence_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'ec_number_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'EC_NUMBER', locus_ids, name='convert.from_backend.ec_number_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_ecnumber_data_backend_starter(nex_backend, 'ec_number_details', ecnumber_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'EC_NUMBER_LOCUS', ecnumber_ids, name='convert.from_backend.ec_number_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'go_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'GO', locus_ids, name='convert.from_backend.go_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_go_data_backend_starter(nex_backend, 'go_details', go_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'GO_LOCUS', go_ids, name='convert.from_backend.go_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_go_data_with_children_backend_starter(nex_backend, 'go_details', go_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'GO_LOCUS_ALL_CHILDREN', go_ids, name='convert.from_backend.go_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_reference_data_backend_starter(nex_backend, 'go_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'GO', reference_ids, name='convert.from_backend.go_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'interaction_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'INTERACTION', locus_ids, name='convert.from_backend.interaction_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_reference_data_backend_starter(nex_backend, 'interaction_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'INTERACTION', reference_ids, name='convert.from_backend.interaction_details', commit_interval=1000),
    #                 OutputTransformer(1000)])

    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'literature_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'LITERATURE', locus_ids, name='convert.from_backend.literature_details', commit_interval=1000),
    #                 OutputTransformer(1000)])

    # do_conversion(make_reference_data_backend_starter(nex_backend, 'literature_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'LITERATURE', reference_ids, name='convert.from_backend.literature_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'protein_domain_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PROTEIN_DOMAIN', locus_ids, name='convert.from_backend.protein_domain_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_domain_data_backend_starter(nex_backend, 'protein_domain_details', domain_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'PROTEIN_DOMAIN_LOCUS', domain_ids, name='convert.from_backend.protein_domain_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'protein_phosphorylation_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PROTEIN_PHOSPHORYLATION', locus_ids, name='convert.from_backend.protein_phosphorylation_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'protein_experiment_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PROTEIN_EXPERIMENT', locus_ids, name='convert.from_backend.protein_experiment_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'phenotype_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'PHENOTYPE', locus_ids, name='convert.from_backend.phenotype_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_phenotype_data_backend_starter(nex_backend, 'phenotype_details', phenotype_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'PHENOTYPE_LOCUS', phenotype_ids, name='convert.from_backend.phenotype_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_reference_data_backend_starter(nex_backend, 'phenotype_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'PHENOTYPE', reference_ids, name='convert.from_backend.phenotype_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_chemical_data_backend_starter(nex_backend, 'phenotype_details', chemical_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'PHENOTYPE', chemical_ids, name='convert.from_backend.phenotype_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_observable_data_backend_starter(nex_backend, 'phenotype_details', observable_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptDetails, 'OBSERVABLE_LOCUS', observable_ids, name='convert.from_backend.phenotype_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'regulation_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'REGULATION', locus_ids, name='convert.from_backend.regulation_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_reference_data_backend_starter(nex_backend, 'regulation_details', reference_ids),
    #                [Json2DataPerfDB(perf_session_maker, ReferenceDetails, 'REGULATION', reference_ids, name='convert.from_backend.regulation_details', commit_interval=1000),
    #                 OutputTransformer(1000)])

    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'regulation_target_enrichment', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityEnrichment, 'REGULATION', locus_ids, name='convert.from_backend.regulation_target_enrichment', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'binding_site_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'BINDING_SITE', locus_ids, name='convert.from_backend.binding_site_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'phenotype_graph', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'PHENOTYPE', locus_ids, name='convert.from_backend.phenotype_graph', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'go_graph', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'GO', locus_ids, name='convert.from_backend.go_graph', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'protein_domain_graph', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'PROTEIN_DOMAIN', locus_ids, name='convert.from_backend.protein_domain_graph', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'literature_graph', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'LITERATURE', locus_ids, name='convert.from_backend.literature_graph', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'regulation_graph', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'REGULATION', locus_ids, name='convert.from_backend.regulation_graph', commit_interval=1000),
    #                 OutputTransformer(1000)])

    # do_conversion(make_locus_data_backend_starter(nex_backend, 'expression_graph', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'EXPRESSION', locus_ids, name='convert.from_backend.expression_graph', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_go_data_backend_starter(nex_backend, 'go_ontology_graph', go_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptGraph, 'GO_ONTOLOGY', go_ids, name='convert.from_backend.go_ontology_graph', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # Done
    # do_conversion(make_observable_data_backend_starter(nex_backend, 'phenotype_ontology_graph', observable_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioconceptGraph, 'PHENOTYPE_ONTOLOGY', observable_ids, name='convert.from_backend.phenotype_ontology_graph', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_orphan_backend_starter(nex_backend, ['references_this_week']),
    #                [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'expression_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'EXPRESSION', locus_ids, name='convert.from_backend.expression_details', commit_interval=100),
    #                 OutputTransformer(100)])
    #
    # do_conversion(make_orphan_backend_starter(nex_backend, ['references_this_week', 'all_locus']),
    #                [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])

    # do_conversion(make_orphan_backend_starter(nex_backend, ['references_this_week']),
    #                [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000, )])
    # do_conversion(make_orphan_backend_starter(nex_backend, ['all_locus']),
    #                [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])
    do_conversion(make_orphan_backend_starter(nex_backend, ['go_snapshot']),
                   [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])
    do_conversion(make_orphan_backend_starter(nex_backend, ['phenotype_snapshot']),
                   [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])

    # locus_types = ['ORF', 'long_terminal_repeat', 'ARS', 'tRNA', 'transposable_element_gene', 'snoRNA', 'retrotransposon', 'telomere', 'rRNA', 'pseudogene', 'ncRNA', 'centromere', 'snRNA', 'multigene locus', 'gene_cassette', 'mating_locus']
    # do_conversion(make_orphan_arg_backend_starter(nex_backend, 'obj_list', locus_types),
    #               [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])
    #
    # do_conversion(make_orphan_arg_backend_starter(nex_backend, 'obj_list', ['tag']),
    #                [Json2OrphanPerfDB(perf_session_maker, name='convert.from_backend.orphans', commit_interval=1000)])
