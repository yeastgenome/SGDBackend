from src.sgd.model import bud, nex
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, OutputTransformer
__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    # # ------------------------------------------ Evelements ------------------------------------------
    # # Bud -> Nex
    # from src.sgd.model.nex.misc import Source, Strain, Experiment, Experimentalias, Experimentrelation, Url, Alias, Relation, Strainurl
    # from src.sgd.model.nex.auxiliary import Disambig
    # from src.sgd.convert.from_bud.evelements import make_source_starter, make_strain_starter, make_experiment_starter, \
    #     make_experiment_alias_starter, make_experiment_relation_starter, make_strain_url_starter
    # from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
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
    # # ------------------------------------------ Bioentity ------------------------------------------
    # # Bud -> Nex
    # from src.sgd.model.nex.bioentity import Bioentity, Locus, Complex, Bioentityalias, Bioentityrelation, Bioentityurl
    # from src.sgd.model.nex.misc import Alias, Relation, Url
    # from src.sgd.model.nex.auxiliary import Locustabs, Disambig
    # from src.sgd.convert.from_bud.bioentity import make_locus_starter, make_complex_starter, make_bioentity_tab_starter, \
    #     make_bioentity_alias_starter, make_bioentity_relation_starter, make_bioentity_url_starter
    # from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
    #
    # do_conversion(make_locus_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Locus),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Locus), name='convert.from_bud.bioentity.locus', delete_untouched=True, commit=True)])
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

    # ------------------------------------------ Bioconcept ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.bioconcept import Bioconcept, Observable, Phenotype, Go, ECNumber, Bioconceptalias, Bioconceptrelation, Bioconcepturl
    from src.sgd.model.nex.misc import Alias, Relation, Url
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.convert.from_bud.bioconcept import make_phenotype_starter, make_go_starter, \
        make_ecnumber_starter, make_bioconcept_alias_starter, make_bioconcept_relation_starter, make_observable_starter, make_bioconcept_url_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter

    do_conversion(make_observable_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Observable),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Observable), name='convert.from_bud.bioconcept.observable', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Observable, Bioconcept, 'OBSERVABLE')

    do_conversion(make_phenotype_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Phenotype),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Phenotype), name='convert.from_bud.bioconcept.phenotype', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Phenotype, Bioconcept, 'PHENOTYPE')

    do_conversion(make_go_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Go),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Go), name='convert.from_bud.bioconcept.go', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Go, Bioconcept, 'GO')

    do_conversion(make_ecnumber_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(ECNumber),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(ECNumber), name='convert.from_bud.bioconcept.ecnumber', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, ECNumber, Bioconcept, 'EC_NUMBER')

    do_conversion(make_bioconcept_relation_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioconceptrelation),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconceptrelation), name='convert.from_bud.bioconcept.relation', commit_interval=1000, delete_untouched=True),
                   OutputTransformer(10000)])
    clean_up_orphans(nex_session_maker, Bioconceptrelation, Relation, 'BIOCONCEPT')

    do_conversion(make_bioconcept_alias_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioconceptalias),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconceptalias), name='convert.from_bud.bioconcept.alias', commit_interval=1000, delete_untouched=True),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Bioconceptalias, Alias, 'BIOCONCEPT')

    do_conversion(make_bioconcept_url_starter(nex_session_maker),
                  [Json2Obj(Bioconcepturl),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconcepturl), name='convert.from_bud.bioconcept.url', commit_interval=1000, delete_untouched=True),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Bioconcepturl, Url, 'BIOCONCEPT')

    do_conversion(make_disambig_starter(nex_session_maker, ECNumber, ['id', 'format_name'], 'BIOCONCEPT', 'ECNUMBER'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'ECNUMBER'), name='convert.from_bud.bioconcept.disambig.ecnumber', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Observable, ['id', 'format_name'], 'BIOCONCEPT', 'OBSERVABLE'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'OBSERVABLE'), name='convert.from_bud.bioconcept.disambig.observable', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Phenotype, ['id', 'format_name'], 'BIOCONCEPT', 'PHENOTYPE'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'PHENOTYPE'), name='convert.from_bud.bioconcept.disambig.phenotype', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Go, ['id', 'format_name'], 'BIOCONCEPT', 'GO'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOCONCEPT').filter(Disambig.subclass_type == 'GO'), name='convert.from_bud.bioconcept.disambig.go', delete_untouched=True, commit=True)])

    # ------------------------------------------ Bioitem ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.bioitem import Bioitem, Orphanbioitem, Domain, Allele, Chemical, Bioitemurl, Bioitemrelation, \
        Bioitemalias, Contig
    from src.sgd.model.nex.misc import Alias, Relation, Url
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.convert.from_bud.bioitem import make_allele_starter, make_chemical_starter, make_domain_starter, \
        make_orphan_starter, make_contig_starter, make_bioitem_url_starter, make_bioitem_relation_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter

    do_conversion(make_orphan_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Orphanbioitem),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Orphanbioitem), name='convert.from_bud.bioitem.orphan', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Orphanbioitem, Bioitem, 'ORPHAN')

    do_conversion(make_allele_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Allele),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Allele), name='convert.from_bud.bioitem.allele', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Allele, Bioitem, 'ALLELE')

    do_conversion(make_domain_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Domain),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Domain), name='convert.from_bud.bioitem.domain', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Domain, Bioitem, 'DOMAIN')

    do_conversion(make_chemical_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Chemical),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Chemical), name='convert.from_bud.bioitem.chemical', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Chemical, Bioitem, 'CHEMICAL')

    do_conversion(make_contig_starter(nex_session_maker),
                  [Json2Obj(Contig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Contig), name='convert.from_bud.bioitem.contig', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Contig, Bioitem, 'CONTIG')

    do_conversion(make_bioitem_relation_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioitemrelation),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemrelation), name='convert.from_bud.bioitem.relation', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Bioitemrelation, Relation, 'BIOITEM')

    do_conversion(make_bioitem_url_starter(nex_session_maker),
                  [Json2Obj(Bioitemurl),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemurl), name='convert.from_bud.bioitem.url', delete_untouched=True, commit=True)])
    clean_up_orphans(nex_session_maker, Bioitemurl, Url, 'BIOITEM')

    do_conversion(make_disambig_starter(nex_session_maker, Domain, ['id', 'format_name'], 'BIOITEM', 'DOMAIN'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'DOMAIN'), name='convert.from_bud.bioitem.disambig.domain', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Chemical, ['id', 'format_name'], 'BIOITEM', 'CHEMICAL'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'CHEMICAL'), name='convert.from_bud.bioitem.disambig.chemical', delete_untouched=True, commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Contig, ['id', 'format_name'], 'BIOITEM', 'CONTIG'),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'CONTIG'), name='convert.from_bud.bioitem.disambig.contig', delete_untouched=True, commit=True)])

    # ------------------------------------------ Paragraph ------------------------------------------
    from src.sgd.model.nex.paragraph import Paragraph, ParagraphReference, Bioentityparagraph, Strainparagraph, Referenceparagraph
    from src.sgd.model.nex.misc import Source
    from src.sgd.convert.from_bud.paragraph import make_paragraph_reference_starter, make_bioentity_paragraph_starter, \
        make_strain_paragraph_starter, make_reference_paragraph_starter

    do_conversion(make_bioentity_paragraph_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bioentityparagraph),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityparagraph), name='convert.from_bud.paragraph.bioentity', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Bioentityparagraph, Paragraph, 'BIOENTITY')

    do_conversion(make_strain_paragraph_starter(nex_session_maker),
                  [Json2Obj(Strainparagraph),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Strainparagraph), name='convert.from_bud.paragraph.strain', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Strainparagraph, Paragraph, 'STRAIN')

    do_conversion(make_reference_paragraph_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Referenceparagraph),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Referenceparagraph), name='convert.from_bud.paragraph.reference', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Referenceparagraph, Paragraph, 'REFERENCE')

    do_conversion(make_paragraph_reference_starter(nex_session_maker),
                  [Json2Obj(ParagraphReference),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(ParagraphReference), name='convert.from_bud.paragraph_reference', delete_untouched=True, commit=True),
                   OutputTransformer(1000)])