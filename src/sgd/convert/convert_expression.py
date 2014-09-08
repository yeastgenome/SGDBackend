from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Json2Obj, Json2DataPerfDB, \
    make_locus_data_backend_starter, make_reference_data_backend_starter, Evidence2NexDB, BigObj2NexDB
from src.sgd.convert.transformers import do_conversion, Json2Obj, Obj2NexDB

__author__ = 'kpaskov'

if __name__ == "__main__":

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evidence ------------------------------------------
    from src.sgd.model.nex.bioitem import Dataset, Datasetcolumn
    from src.sgd.model.nex.evidence import Evidence, Expressionevidence, Bioentitydata
    from src.sgd.model.nex.auxiliary import Bioentityinteraction
    from src.sgd.convert.from_bud.evidence import make_expression_data_starter, make_expression_evidence_starter
    from src.sgd.convert.from_bud.auxiliary import make_bioentity_expression_interaction_starter
    import os

    # do_conversion(make_expression_evidence_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14'),
    #               [Json2Obj(Expressionevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Expressionevidence),
    #                          name='convert.from_bud.evidence.expression',
    #                          delete_untouched=False,
    #                          commit_interval=1000,
    #                          already_deleted=clean_up_orphans(nex_session_maker, Expressionevidence, Evidence, 'EXPRESSION'))])

    #
    # nex_session = nex_session_maker()
    # dataset_key_to_id = dict([(x.unique_key(), x.id) for x in nex_session.query(Dataset).all()])
    # dataset_id_to_columns = dict([(x, []) for x in dataset_key_to_id.values()])
    #
    # for datasetcolumn in nex_session.query(Datasetcolumn).all():
    #     if datasetcolumn.dataset_id in dataset_id_to_columns:
    #         dataset_id_to_columns[datasetcolumn.dataset_id].append(datasetcolumn.id)
    #
    # datasetcolumn_id_to_evidence_id = dict()
    # for expressionevidence in nex_session.query(Expressionevidence).all():
    #     datasetcolumn_id_to_evidence_id[expressionevidence.datasetcolumn_id] = expressionevidence.id
    #
    #
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
    #             dataset_key = (file[:-4], 'DATASET')
    #
    #             do_conversion(make_expression_data_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14/' + path + '/' + file, dataset_key_to_id[dataset_key], dataset_key_to_channel_count[dataset_key], key_to_locus, aliases),
    #                                   [Json2Obj(Bioentitydata),
    #                                    Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentitydata).filter(Bioentitydata.evidence_id.in_([datasetcolumn_id_to_evidence_id[y] for y in dataset_id_to_columns[dataset_key_to_id[dataset_key]]])),
    #                                              name='convert.from_bud.evidence.expression_data',
    #                                              delete_untouched=True,
    #                                              commit_interval=1000)])

    # do_conversion(make_bioentity_expression_interaction_starter(nex_session_maker),
    #               [Json2Obj(Bioentityinteraction),
    #                BigObj2NexDB(nex_session_maker, lambda x: x.query(Bioentityinteraction).filter_by(interaction_type='EXPRESSION'),
    #                             name='convert.from_bud.auxilliary.bioentity_interaction_expression',
    #                             delete_untouched=True,
    #                             commit_interval=1000)])

    # ------------------------------------------ Perf ------------------------------------------

    from src.sgd.model.perf.bioentity_data import BioentityGraph

    from src.sgd.model.nex.bioentity import Locus
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    nex_session.close()

    do_conversion(make_locus_data_backend_starter(nex_backend, 'expression_graph', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityGraph,
                                    'EXPRESSION',
                                    locus_ids,
                                    name='convert.from_backend.expression_graph',
                                    commit_interval=1000)])


    # ------------------------------------------ Perf2 ------------------------------------------
