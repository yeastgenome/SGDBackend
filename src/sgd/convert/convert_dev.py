from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, OutputTransformer, make_file_starter, \
    make_backend_starter, Json2CorePerfDB


__author__ = 'kpaskov'

if __name__ == "__main__":   

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # # ------------------------------------------ Evelements ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.misc import Source, Strain, Experiment, Experimentalias, Experimentrelation, Url, Alias, Relation, Strainurl
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.model.perf.core import Strain as PerfStrain
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

    # # Nex -> Perf
    # do_conversion(make_backend_starter(nex_backend, 'all_strains', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfStrain, name='convert.from_backend.strain', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])

    # # ------------------------------------------ Bioentity ------------------------------------------
    # # Bud -> Nex
    from src.sgd.model.nex.bioentity import Bioentity, Locus, Complex, Bioentityalias, Bioentityrelation, Bioentityurl
    from src.sgd.model.nex.misc import Alias, Relation, Url
    from src.sgd.model.nex.auxiliary import Locustabs, Disambig
    from src.sgd.model.perf.core import Bioentity as PerfBioentity
    from src.sgd.convert.from_bud.bioentity import make_locus_starter, make_complex_starter, make_bioentity_tab_starter, \
        make_bioentity_alias_starter, make_bioentity_relation_starter, make_bioentity_url_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
    #
    # do_conversion(make_locus_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Locus),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Locus), name='convert.from_bud.bioentity.locus', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Locus, Bioentity, 'LOCUS')
    #
    # do_conversion(make_complex_starter(bud_session_maker, nex_session_maker),
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
    #
    # Nex -> Perf
    # do_conversion(make_backend_starter(nex_backend, 'all_bioentities', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioentity, name='convert.from_backend.bioentity', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])

    # ------------------------------------------ Bioconcept ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.bioconcept import Bioconcept, Observable, Phenotype, Go, ECNumber, Bioconceptalias, Bioconceptrelation
    from src.sgd.model.nex.misc import Alias, Relation
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.model.perf.core import Bioconcept as PerfBioconcept
    from src.sgd.convert.from_bud.bioconcept import make_phenotype_starter, make_go_starter, \
        make_ecnumber_starter, make_bioconcept_alias_starter, make_bioconcept_relation_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter

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
    #
    # # Nex -> Perf
    # do_conversion(make_backend_starter(nex_backend, 'all_bioconcepts', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioconcept, name='convert.from_backend.bioconcept', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])

    # # ------------------------------------------ Bioitem ------------------------------------------
    # # Bud -> Nex
    from src.sgd.model.nex.bioitem import Bioitem, Orphanbioitem, Domain, Allele, Chemical, Bioitemurl, Bioitemrelation, \
        Bioitemalias, Contig
    from src.sgd.model.nex.misc import Alias, Relation, Url
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.model.perf.core import Bioitem as PerfBioitem
    from src.sgd.convert.from_bud.bioitem import make_allele_starter, make_chemical_starter, make_domain_starter, \
        make_orphan_starter, make_contig_starter, make_bioitem_url_starter, make_bioitem_relation_starter
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
    #
    # do_conversion(make_bioitem_relation_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioitemrelation),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemrelation), name='convert.from_bud.bioitem.relation', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bioitemrelation, Relation, 'BIOITEM')
    #
    # do_conversion(make_bioitem_url_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Bioitemurl),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemurl), name='convert.from_bud.bioitem.url', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bioitemurl, Url, 'BIOITEM')
    #
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
    # # Nex -> Perf
    # do_conversion(make_backend_starter(nex_backend, 'all_bioitems', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfBioitem, name='convert.from_backend.bioitem', commit_interval=1000, delete_untouched=True),
    #                OutputTransformer(1000)])

    # ------------------------------------------ Reference ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.reference import Reference, Journal, Book, Author, Referencealias, Referenceurl, \
        Referencerelation, Bibentry, AuthorReference, ReferenceReftype, Reftype
    from src.sgd.model.nex.misc import Alias, Relation, Url
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.model.perf.core import Reference as PerfReference, Author as PerfAuthor
    from src.sgd.convert.from_bud.reference import make_reference_starter, make_journal_starter, make_book_starter,\
        make_bibentry_starter, make_reftype_starter, make_reference_alias_starter, \
        make_author_reference_starter, make_author_starter, make_ref_reftype_starter, make_reference_relation_starter, \
        make_reference_url_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
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
    #
    # # # Nex -> Perf
    # do_conversion(make_backend_starter(nex_backend, 'all_references', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfReference, name='convert.from_backend.reference', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    #
    # do_conversion(make_backend_starter(nex_backend, 'all_authors', 1000),
    #               [Json2CorePerfDB(perf_session_maker, PerfAuthor, name='convert.from_backend.author', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])

    # ------------------------------------------ Evidence ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.evidence import Evidence, Goevidence, DNAsequenceevidence, Regulationevidence, \
        Proteinsequenceevidence, Phosphorylationevidence, Domainevidence, Literatureevidence, Phenotypeevidence, DNAsequencetag
    from src.sgd.convert.from_bud.evidence import make_go_evidence_starter, make_dna_sequence_evidence_starter, \
        make_regulation_evidence_starter, make_protein_sequence_evidence_starter, make_phosphorylation_evidence_starter, \
        make_domain_evidence_starter, make_literature_evidence_starter, make_phenotype_evidence_starter, make_dna_sequence_tag_starter
    # do_conversion(make_alias_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Aliasevidence),
    #                 Obj2NexDB(nex_session_maker, lambda x: x.query(Aliasevidence), name='convert.from_bud.evidence.alias', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Aliasevidence, Evidence, 'ALIAS')
    #
    # do_conversion(make_binding_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Bindingevidence),
    #                 Obj2NexDB(nex_session_maker, lambda x: x.query(Bindingevidence), name='convert.from_bud.evidence.binding', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bindingevidence, Evidence, 'BINDING')
    #
    # do_conversion(make_bioentity_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Bioentityevidence),
    #                 Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityevidence), name='convert.from_bud.evidence.bioentity', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Bioentityevidence, Evidence, 'BIOENTITY')
    #
    # do_conversion(make_complex_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Complexevidence),
    #                 Obj2NexDB(nex_session_maker, lambda x: x.query(Complexevidence), name='convert.from_bud.evidence.complex', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, Complexevidence, Evidence, 'COMPLEX')
    #
    # do_conversion(make_domain_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Domainevidence),
    #                 Obj2NexDB(nex_session_maker, lambda x: x.query(Domainevidence), name='convert.from_bud.evidence.domain', delete_untouched=True, commit=True),
    #                 OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Domainevidence, Evidence, 'DOMAIN')

    # do_conversion(make_ecnumber_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(ECNumberevidence),
    #                 Obj2NexDB(nex_session_maker, lambda x: x.query(ECNumberevidence), name='convert.from_bud.evidence.ecnumber', delete_untouched=True, commit=True)])
    # clean_up_orphans(nex_session_maker, ECNumberevidence, Evidence, 'ECNUMBER')
    #
    # do_conversion(make_go_evidence_starter(bud_session_maker, nex_session_maker),
    #                [Json2Obj(Goevidence),
    #                 Obj2NexDB(nex_session_maker, lambda x: x.query(Goevidence), name='convert.from_bud.evidence.go', delete_untouched=True, commit_interval=1000),
    #                 OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Goevidence, Evidence, 'GO')
    #
    # do_conversion(make_interaction_evidence_starter(bud_session_maker, nex_session_maker, 'genetic interactions'),
    #               [Json2Obj(Geninteractionevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Geninteractionevidence), name='convert.from_bud.evidence.geninteraction', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Geninteractionevidence, Evidence, 'GENINTERACTION')
    # #
    # do_conversion(make_interaction_evidence_starter(bud_session_maker, nex_session_maker, 'physical interactions'),
    #               [Json2Obj(Physinteractionevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Physinteractionevidence), name='convert.from_bud.evidence.physinteraction', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Physinteractionevidence, Evidence, 'PHYSINTERACTION')
    #
    # do_conversion(make_literature_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Literatureevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Literatureevidence), name='convert.from_bud.evidence.literature', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Literatureevidence, Evidence, 'LITERATURE')
    #
    # do_conversion(make_archive_literature_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(ArchiveLiteratureevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(ArchiveLiteratureevidence), name='convert.from_bud.evidence.archive_literature', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, ArchiveLiteratureevidence, Evidence, 'ARCH_LITERATURE')
    #
    # do_conversion(make_phenotype_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Phenotypeevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Phenotypeevidence), name='convert.from_bud.evidence.phenotype', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Phenotypeevidence, Evidence, 'PHENOTYPE')
    #
    # do_conversion(make_phosphorylation_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Phosphorylationevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Phosphorylationevidence), name='convert.from_bud.evidence.phosphorylation', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Phosphorylationevidence, Evidence, 'PHOSPHORYLATION')
    #
    # do_conversion(make_protein_experiment_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Proteinexperimentevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Proteinexperimentevidence), name='convert.from_bud.evidence.protein_experiment', delete_untouched=True, commit=True),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Proteinexperimentevidence, Evidence, 'PROTEINEXPERIMENT')
    #
    # do_conversion(make_regulation_evidence_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Regulationevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Regulationevidence), name='convert.from_bud.evidence.regulation', delete_untouched=True, commit_interval=1000),
    #                OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Regulationevidence, Evidence, 'REGULATION')
    #
    from src.sgd.convert.from_bud import sequence_files, protein_sequence_files
    from src.sgd.model.nex.misc import Strain
    nex_session = nex_session_maker()
    strain_key_to_id = dict([(x.unique_key(), x.id) for x in nex_session.query(Strain).all()])
    nex_session.close()
    #
    for sequence_filename, coding_sequence_filename, strain_key in sequence_files:
        do_conversion(make_dna_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, coding_sequence_filename),
                      [Json2Obj(DNAsequenceevidence),
                       Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.strain_id == strain_key_to_id[strain_key]), name='convert.from_bud.evidence.dnasequence', delete_untouched=True, commit_interval=1000),
                       OutputTransformer(1000)])

        if strain_key == 'S288C':
            do_conversion(make_dna_sequence_tag_starter(nex_session_maker, strain_key, sequence_filename),
                          [Json2Obj(DNAsequencetag),
                           Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequencetag), name='convert.from_bud.evidence.dnasequence.tags', delete_untouched=True, commit_interval=1000),
                           OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, DNAsequenceevidence, Evidence, 'DNASEQUENCE')

    #
    # protparam_data = dict([(row[0], row) for row in make_file_starter('src/sgd/convert/data/ProtParam.txt')()])
    # for sequence_filename, strain_key in protein_sequence_files:
    #     do_conversion(make_protein_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, protparam_data),
    #                   [Json2Obj(Proteinsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(Proteinsequenceevidence).filter(Proteinsequenceevidence.strain_id == strain_key_to_id[strain_key]), name='convert.from_bud.evidence.proteinsequence', delete_untouched=True, commit_interval=1000),
    #                    OutputTransformer(1000)])
    # clean_up_orphans(nex_session_maker, Proteinsequenceevidence, Evidence, 'PROTEINSEQUENCE')
    #
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
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityparagraph), name='convert.from_bud.paragraph.bioentity', delete_untouched=True, commit=True),
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

    # # ------------------------------------------ Auxilliary ------------------------------------------
    # from src.sgd.model.nex.auxiliary import Interaction, Bioentityinteraction, Bioconceptinteraction, Referenceinteraction
    # from src.sgd.convert.from_bud.auxiliary import make_bioentity_interaction_starter, \
    #     make_bioconcept_interaction_starter, make_reference_interaction_starter
    #
    # do_conversion(make_bioentity_interaction_starter(nex_session_maker),
    #               [Json2Obj(Bioentityinteraction),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityinteraction), name='convert.from_bud.auxilliary.bioentity_interaction', delete_untouched=True, commit_interval=1000),
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

    # # ------------------------------------------ Perf ------------------------------------------
    # from src.sgd.model.perf.core import Disambig as PerfDisambig
    # do_conversion(make_backend_starter(nex_backend, 'all_disambigs', 1000),
    #                [Json2CorePerfDB(perf_session_maker, PerfDisambig, name='convert.from_backend.disambig', commit_interval=1000, delete_untouched=True),
    #                 OutputTransformer(1000)])