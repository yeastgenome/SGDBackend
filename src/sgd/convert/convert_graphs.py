from src.sgd.model import nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, OutputTransformer, \
    make_individual_locus_backend_starter, Json2DataPerfDB, make_individual_complex_backend_starter, \
    make_individual_go_backend_starter, make_individual_observable_backend_starter

__author__ = 'kpaskov'

if __name__ == "__main__":   

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Auxilliary ------------------------------------------
    from src.sgd.model.nex.auxiliary import Interaction, Bioentityinteraction, Bioconceptinteraction, Referenceinteraction, Bioiteminteraction
    from src.sgd.convert.from_bud.auxiliary import make_bioentity_interaction_starter, \
        make_bioconcept_interaction_starter, make_reference_interaction_starter, make_bioitem_interaction_starter

    do_conversion(make_bioentity_interaction_starter(nex_session_maker),
                  [Json2Obj(Bioentityinteraction),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentityinteraction), name='convert.from_bud.auxilliary.bioentity_interaction', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Bioentityinteraction, Interaction, 'BIOENTITY')

    do_conversion(make_bioconcept_interaction_starter(nex_session_maker),
                  [Json2Obj(Bioconceptinteraction),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioconceptinteraction), name='convert.from_bud.auxilliary.bioconcept_interaction', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Bioconceptinteraction, Interaction, 'BIOCONCEPT')

    do_conversion(make_reference_interaction_starter(nex_session_maker),
                  [Json2Obj(Referenceinteraction),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Referenceinteraction), name='convert.from_bud.auxilliary.reference_interaction', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Referenceinteraction, Interaction, 'REFERENCE')

    do_conversion(make_bioitem_interaction_starter(nex_session_maker),
                  [Json2Obj(Bioiteminteraction),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bioiteminteraction), name='convert.from_bud.auxilliary.bioitem_interaction', delete_untouched=True, commit_interval=1000),
                   OutputTransformer(1000)])
    clean_up_orphans(nex_session_maker, Bioiteminteraction, Interaction, 'BIOITEM')

    # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityGraph
    from src.sgd.model.perf.bioconcept_data import BioconceptGraph

    from src.sgd.model.nex.bioentity import Locus, Complex
    from src.sgd.model.nex.bioconcept import Go, Observable
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    complex_ids = [x.id for x in nex_session.query(Complex).all()]
    go_ids = [x.id for x in nex_session.query(Go).all()]
    observable_ids = [x.id for x in nex_session.query(Observable).all()]
    nex_session.close()

    do_conversion(make_individual_locus_backend_starter(nex_backend, 'phenotype_graph', 'PHENOTYPE', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'PHENOTYPE', name='convert.from_backend.phenotype_graph', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])

    do_conversion(make_individual_locus_backend_starter(nex_backend, 'go_graph', 'GO', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'GO', name='convert.from_backend.go_graph', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])

    do_conversion(make_individual_locus_backend_starter(nex_backend, 'protein_domain_graph', 'PROTEIN_DOMAIN', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'PROTEIN_DOMAIN', name='convert.from_backend.protein_domain_graph', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])

    do_conversion(make_individual_locus_backend_starter(nex_backend, 'literature_graph', 'LITERATURE', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'LITERATURE', name='convert.from_backend.literature_graph', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])

    do_conversion(make_individual_locus_backend_starter(nex_backend, 'regulation_graph', 'REGULATION', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'REGULATION', name='convert.from_backend.regulation_graph', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])

    do_conversion(make_individual_complex_backend_starter(nex_backend, 'complex_graph', 'COMPLEX', complex_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'COMPLEX', name='convert.from_backend.complex_graph', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])

    do_conversion(make_individual_go_backend_starter(nex_backend, 'go_ontology_graph', 'ONTOLOGY', go_ids),
                   [Json2DataPerfDB(perf_session_maker, BioconceptGraph, 'ONTOLOGY', name='convert.from_backend.go_ontology_graph', attr_name='bioconcept_id', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])

    do_conversion(make_individual_observable_backend_starter(nex_backend, 'phenotype_ontology_graph', 'ONTOLOGY', observable_ids),
                   [Json2DataPerfDB(perf_session_maker, BioconceptGraph, 'ONTOLOGY', name='convert.from_backend.phenotype_ontology_graph', attr_name='bioconcept_id', commit_interval=1000, delete_untouched=True),
                    OutputTransformer(1000)])