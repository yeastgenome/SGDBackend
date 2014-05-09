from src.sgd.convert import config

__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf1_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    perf2_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Bioentity ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.bioentity import Locus, Complex, Bioentityalias, Bioentityrelation, Bioentityurl

    do_conversion(make_locus_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Locus),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Locus), name='convert.from_bud.bioentity.locus', delete_untouched=True, commit=True)])

    do_conversion(make_complex_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Complex),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Complex), name='convert.from_bud.bioentity.complex', delete_untouched=True, commit=True)])

    do_conversion(make_bioentity_tab_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Locustabs),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Locustabs), name='convert.from_bud.bioentity.locustabs', delete_untouched=True, commit=True)])

    do_conversion(make_bioentity_alias_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioentityalias),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityalias), name='convert.from_bud.bioentity.alias', delete_untouched=True, commit=True)])

    do_conversion(make_bioentity_relation_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioentityrelation),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityrelation), name='convert.from_bud.bioentity.relation', delete_untouched=True, commit=True)])

    do_conversion(make_bioentity_url_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioentityurl),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityurl), name='convert.from_bud.bioentity.url', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])

    do_conversion(make_disambig_starter(nex_session_maker, Locus, ['id', 'format_name', 'display_name', 'sgdid'], 'BIOENTITY', 'LOCUS'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOENTITY').filter(Disambig.subclass_type == 'LOCUS'), name='convert.from_bud.bioentity.disambig.locus', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Complex, ['id', 'format_name'], 'BIOENTITY', 'COMPLEX'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOENTITY').filter(Disambig.subclass_type == 'COMPLEX'), name='convert.from_bud.bioentity.disambig.complex', delete_untouched=True, commit=True)])

    # Nex -> Perf
    from src.sgd.model.perf.core import Bioentity as PerfBioentity
    do_conversion(make_backend_starter(nex_backend, 'all_bioentities', 1000),
                  [Json2Obj(PerfBioentity),
                   Obj2CorePerfDB(perf_session_maker, PerfBioentity, name='convert.from_backend.bioentity', commit_interval=1000, delete_untouched=True),
                   OutputTransformer(1000)])

    # ------------------------------------------ Bioconcept ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.bioconcept import Observable, Phenotype, Go, ECNumber, Bioconceptrelation, Bioconceptalias
    do_conversion(make_observable_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Observable),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Observable), name='convert.from_bud.bioconcept.observable', delete_untouched=True, commit=True)])

    do_conversion(make_phenotype_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Phenotype),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Phenotype), name='convert.from_bud.bioconcept.phenotype', delete_untouched=True, commit=True)])

    do_conversion(make_go_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Go),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Go), name='convert.from_bud.bioconcept.go', delete_untouched=True, commit=True)])

    do_conversion(make_ecnumber_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(ECNumber),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(ECNumber), name='convert.from_bud.bioconcept.ecnumber', delete_untouched=True, commit=True)])

    do_conversion(make_bioconcept_relation_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioconceptrelation),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconceptrelation), name='convert.from_bud.bioconcept.relation', commit_interval=1000, delete_untouched=True),
                   OutputTransformer(1000)])

    do_conversion(make_bioconcept_alias_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioconceptalias),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconceptalias), name='convert.from_bud.bioconcept.alias', commit_interval=1000, delete_untouched=True),
                   OutputTransformer(1000)])

    do_conversion(make_disambig_starter(nex_session_maker, ECNumber, ['id', 'format_name'], 'BIOCONCEPT', 'ECNUMBER'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'ECNUMBER'), name='convert.from_bud.bioconcept.disambig.ecnumber', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Phenotype, ['id', 'format_name'], 'BIOCONCEPT', 'PHENOTYPE'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'PHENOTYPE'), name='convert.from_bud.bioconcept.disambig.phenotype', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Go, ['id', 'format_name'], 'BIOCONCEPT', 'GO'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'GO'), name='convert.from_bud.bioconcept.disambig.go', delete_untouched=True, commit=True)])

    # Nex -> Perf
    from src.sgd.model.perf.core import Bioconcept as PerfBioconcept
    do_conversion(make_backend_starter(nex_backend, 'all_bioconcepts', 1000),
                  [Json2Obj(PerfBioconcept),
                   Obj2CorePerfDB(perf_session_maker, PerfBioconcept, name='convert.from_backend.bioconcept', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])

    # ------------------------------------------ Bioitem ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.bioitem import Orphanbioitem, Allele, Domain, Chemical, Contig, Bioitemrelation, Bioitemurl
    do_conversion(make_orphan_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Orphanbioitem),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Orphanbioitem), name='convert.from_bud.bioitem.orphan', delete_untouched=True, commit=True)])

    do_conversion(make_allele_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Allele),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Allele), name='convert.from_bud.bioitem.allele', delete_untouched=True, commit=True)])

    do_conversion(make_domain_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Domain),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Domain), name='convert.from_bud.bioitem.domain', delete_untouched=True, commit=True)])

    do_conversion(make_chemical_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Chemical),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Chemical), name='convert.from_bud.bioitem.chemical', delete_untouched=True, commit=True)])

    do_conversion(make_contig_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Contig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Contig), name='convert.from_bud.bioitem.contig', delete_untouched=True, commit=True)])

    do_conversion(make_bioitem_relation_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioitemrelation),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemrelation), name='convert.from_bud.bioitem.relation', delete_untouched=True, commit=True)])

    do_conversion(make_bioitem_url_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioitemurl),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemurl), name='convert.from_bud.bioitem.url', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Domain, ['id', 'format_name'], 'BIOITEM', 'DOMAIN'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'DOMAIN'), name='convert.from_bud.bioitem.disambig.domain', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Chemical, ['id', 'format_name'], 'BIOITEM', 'CHEMICAL'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'CHEMICAL'), name='convert.from_bud.bioitem.disambig.chemical', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Contig, ['id', 'format_name'], 'BIOITEM', 'CONTIG'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'CONTIG'), name='convert.from_bud.bioitem.disambig.contig', delete_untouched=True, commit=True)])

    # Nex -> Perf
    from src.sgd.model.perf.core import Bioitem as PerfBioitem
    do_conversion(make_backend_starter(nex_backend, 'all_bioitems', 1000),
                  [Json2Obj(PerfBioitem),
                   Obj2CorePerfDB(perf_session_maker, PerfBioitem, name='convert.from_backend.bioitem', commit_interval=1000, delete_untouched=True),
                   OutputTransformer(1000)])

    # ------------------------------------------ Evelements ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.misc import Experiment, Strain, Source, Experimentalias, Experimentrelation
    do_conversion(make_experiment_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Experiment),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Experiment), name='convert.from_bud.experiment', delete_untouched=True, commit=True)])

    do_conversion(make_strain_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Strain),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Strain), name='convert.from_bud.strain', delete_untouched=True, commit=True)])

    do_conversion(make_source_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Source),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Source), name='convert.from_bud.source', delete_untouched=True, commit=True)])

    do_conversion(make_experiment_alias_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Experimentalias),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Experimentalias), name='convert.from_bud.experiment_alias', delete_untouched=True, commit=True)])

    do_conversion(make_experiment_relation_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Experimentrelation),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Experimentrelation), name='convert.from_bud.experiment_relation', delete_untouched=True, commit=True)])

    # ------------------------------------------ Reference ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.reference import Journal, Book, Reference, Abstract, Bibentry, Author, AuthorReference, \
        ReferenceReftype, Reftype, Referencerelation, Referencealias, Referenceurl
    do_conversion(make_journal_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Journal),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Journal), name='convert.from_bud.journal', delete_untouched=True, commit=True)])

    do_conversion(make_book_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Book),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Book), name='convert.from_bud.book', delete_untouched=True, commit=True)])

    do_conversion(make_reference_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Reference),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Reference), name='convert.from_bud.reference', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])

    do_conversion(make_abstract_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Abstract),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Abstract), name='convert.from_bud.abstract', delete_untouched=True, commit=True)])

    do_conversion(make_bibentry_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bibentry),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bibentry), name='convert.from_bud.bibentry', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])

    do_conversion(make_author_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Author),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Author), name='convert.from_bud.author', delete_untouched=True, commit=True)])

    do_conversion(make_author_reference_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(AuthorReference),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(AuthorReference), name='convert.from_bud.author_reference', delete_untouched=True, commit=True)])

    do_conversion(make_reftype_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Reftype),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Reftype), name='convert.from_bud.reftype', delete_untouched=True, commit=True)])

    do_conversion(make_ref_reftype_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(ReferenceReftype),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(ReferenceReftype), name='convert.from_bud.reference_reftype', delete_untouched=True, commit=True)])

    do_conversion(make_reference_relation_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Referencerelation),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Referencerelation), name='convert.from_bud.reference_relation', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])

    do_conversion(make_reference_alias_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Referencealias),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Referencealias), name='convert.from_bud.reference_alias', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])

    do_conversion(make_reference_url_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Referenceurl),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Referenceurl), name='convert.from_bud.reference_url', commit_interval=1000, delete_untouched=True),
                   OutputTransformer(1000)])

    do_conversion(make_disambig_starter(nex_session_maker, Reference, ['id', 'sgdid', 'pubmed_id', 'doi'], 'REFERENCE', None),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'REFERENCE'), name='convert.from_bud.reference.disambig', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Author, ['format_name', 'id'], 'AUTHOR', None),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'AUTHOR'), name='convert.from_bud.author.disambig', delete_untouched=True, commit=True)])

    # Nex -> Perf
    from src.sgd.model.perf.core import Reference as PerfReference, Author as PerfAuthor
    do_conversion(make_backend_starter(nex_backend, 'all_references', 1000),
                  [Json2Obj(PerfReference),
                   Obj2CorePerfDB(perf_session_maker, PerfReference, name='convert.from_backend.reference', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])

    do_conversion(make_backend_starter(nex_backend, 'all_authors', 1000),
                  [Json2Obj(PerfAuthor),
                   Obj2CorePerfDB(perf_session_maker, PerfAuthor, name='convert.from_backend.author', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])

    # --------------------------------- Evidence ---------------------------------
    from src.sgd.model.nex.evidence import Aliasevidence, Bioentityevidence, Complexevidence, ECNumberevidence
    do_conversion(make_alias_evidence_starter(bud_session_maker, nex_session_maker),
                   [Json2Obj(Aliasevidence),
                    Obj2NexDB(nex_session_maker, lambda x: x.query(Aliasevidence), name='convert.from_bud.evidence.alias', delete_untouched=True, commit=True)])

    do_conversion(make_bioentity_evidence_starter(bud_session_maker, nex_session_maker),
                   [Json2Obj(Bioentityevidence),
                    Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityevidence), name='convert.from_bud.evidence.bioentity', delete_untouched=True, commit=True)])

    do_conversion(make_complex_evidence_starter(bud_session_maker, nex_session_maker),
                   [Json2Obj(Complexevidence),
                    Obj2NexDB(nex_session_maker, lambda x: x.query(Complexevidence), name='convert.from_bud.evidence.complex', delete_untouched=True, commit=True)])

    do_conversion(make_ecnumber_evidence_starter(bud_session_maker, nex_session_maker),
                   [Json2Obj(ECNumberevidence),
                    Obj2NexDB(nex_session_maker, lambda x: x.query(ECNumberevidence), name='convert.from_bud.evidence.ecnumber', delete_untouched=True, commit=True)])
