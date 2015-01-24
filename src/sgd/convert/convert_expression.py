from src.sgd.model import bud, nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Json2Obj, Json2DataPerfDB, \
    make_locus_data_backend_starter, make_reference_data_backend_starter, Evidence2NexDB, BigObj2NexDB
from src.sgd.convert.transformers import do_conversion, Json2Obj, Obj2NexDB

__author__ = 'kpaskov'

if __name__ == "__main__":

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evidence ------------------------------------------
    from src.sgd.model.nex.bioitem import Dataset, Datasetcolumn, Bioitem, BioitemTag
    from src.sgd.model.nex.evidence import Evidence, Expressionevidence, Bioentitydata
    from src.sgd.model.nex.misc import Tag
    from src.sgd.model.nex.auxiliary import Bioentityinteraction, Disambig
    from src.sgd.convert.from_bud.evidence import make_expression_data_starter, make_expression_evidence_starter
    from src.sgd.convert.from_bud.bioitem import make_dataset_starter, make_datasetcolumn_starter, make_bioitem_tag_starter, make_tag_starter
    from src.sgd.convert.from_bud.auxiliary import make_bioentity_expression_interaction_starter, make_disambig_starter
    import os

    # do_conversion(make_dataset_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14'),
    #               [Json2Obj(Dataset),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Dataset),
    #                          name='convert.from_bud.bioitem.dataset',
    #                          delete_untouched=True,
    #                          commit_interval=1000,
    #                          already_deleted=clean_up_orphans(nex_session_maker, Dataset, Bioitem, 'DATASET'))])
    #
    #
    # do_conversion(make_datasetcolumn_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14'),
    #               [Json2Obj(Datasetcolumn),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Datasetcolumn),
    #                          name='convert.from_bud.bioitem.datasetcolumn',
    #                          delete_untouched=True,
    #                          commit_interval=1000,
    #                          already_deleted=clean_up_orphans(nex_session_maker, Datasetcolumn, Bioitem, 'DATASETCOLUMN'))])

    # do_conversion(make_tag_starter(nex_session_maker),
    #               [Json2Obj(Tag),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Tag),
    #                          name='convert.from_bud.tag',
    #                          delete_untouched=True,
    #                          commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Tag, ['id', 'format_name'], 'TAG', None),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'TAG'),
    #                          name='convert.from_bud.bioitem.disambig.tag',
    #                          delete_untouched=True,
    #                          commit=True)])
    #
    # do_conversion(make_bioitem_tag_starter(nex_session_maker),
    #               [Json2Obj(BioitemTag),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(BioitemTag),
    #                          name='convert.from_bud.bioitem.tag',
    #                          delete_untouched=True,
    #                          commit=True)])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Dataset, ['id', 'format_name'], 'BIOITEM', 'DATASET'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'DATASET'), name='convert.from_bud.bioitem.disambig.dataset', delete_untouched=True, commit=True)])


    # do_conversion(make_expression_evidence_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14'),
    #               [Json2Obj(Expressionevidence),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Expressionevidence),
    #                          name='convert.from_bud.evidence.expression',
    #                          delete_untouched=False,
    #                          commit_interval=1000,
    #                          already_deleted=clean_up_orphans(nex_session_maker, Expressionevidence, Evidence, 'EXPRESSION'))])

#     nex_session = nex_session_maker()
#     dataset_key_to_id = dict([(x.unique_key(), x.id) for x in nex_session.query(Dataset).all()])
#     dataset_id_to_columns = dict([(x, []) for x in dataset_key_to_id.values()])
#
#     for datasetcolumn in nex_session.query(Datasetcolumn).all():
#         if datasetcolumn.dataset_id in dataset_id_to_columns:
#             dataset_id_to_columns[datasetcolumn.dataset_id].append(datasetcolumn.id)
#
#     datasetcolumn_id_to_evidence_id = dict()
#     for expressionevidence in nex_session.query(Expressionevidence).all():
#         datasetcolumn_id_to_evidence_id[expressionevidence.datasetcolumn_id] = expressionevidence.id
#
#
#     dataset_key_to_channel_count = dict([(x.unique_key(), x.channel_count) for x in nex_session.query(Dataset).all()])
#
#     from src.sgd.model.nex.bioentity import Locus, Bioentityalias
#     locuses = nex_session.query(Locus).all()
#     key_to_locus = dict([(x.format_name, x) for x in locuses])
#     key_to_locus.update([(x.display_name, x) for x in locuses])
#     key_to_locus.update([('SGD:' + x.sgdid, x) for x in locuses])
#     aliases = dict()
#     for alias in nex_session.query(Bioentityalias).all():
#         if alias.display_name in aliases:
#             aliases[alias.display_name].add(alias.bioentity)
#         else:
#             aliases[alias.display_name] = set([alias.bioentity])
#     for key, locus in key_to_locus.iteritems():
#         if key in aliases:
#             aliases[key].add(locus)
#
#     new_pcl_files = set(['GSE33929.remapped.final.pcl', 'GSE34117.remapped.final.pcl', 'GSE36599.remapped.final.pcl', 'GSE36955.remapped.final.pcl',
#                         'GSE38260.remapped.final.pcl', 'GSE38478GPL9294.remapped.sfp.pcl', 'GSE38848.remapped.final.pcl',
# 'GSE39861.remapped.final.pcl', 'GSE39903.remapped.final.pcl', 'GSE39950.remapped.final.pcl', 'GSE40116.remapped.final.pcl', 'GSE40351.remapped.final.pcl',
# 'GSE41025.remapped.final.pcl', 'GSE42027.remapped.final.pcl', 'GSE43120.remapped.final.pcl', 'GSE44085.remapped.final.pcl', 'GSE44871.remapped.final.pcl',
# 'GSE45273.remapped.final.pcl', 'GSE45370.remapped.final.pcl', 'GSE45692.remapped.final.pcl', 'GSE45776.remapped.final.pcl', 'GSE47429.remapped.final.pcl',
# 'GSE47712.remapped.final.pcl', 'GSE47820.remapped.final.pcl', 'GSE48956.remapped.final.pcl', 'GSE49340.remapped.final.pcl', 'GSE50186.remapped.final.pcl',
# 'GSE51563.remapped.final.pcl', 'GSE36954.remapped.final.pcl', 'GSE7645.remapped.final.pcl', 'GSE40254.remapped.final.pcl', 'GSE40625.remapped.final.pcl',
# 'GSE41094.remapped.final.pcl', 'GSE42083.remapped.final.pcl', 'GSE44544.remapped.final.pcl', 'GSE49650.remapped.final.pcl', 'GSE50440.remapped.final.pcl',
# 'GSE50947.remapped.final.pcl', 'GSE51613.remapped.final.pcl', 'GSE52189.remapped.final.pcl', 'GSE52256.remapped.final.pcl', 'GSE54196.remapped.final.pcl',
# 'GSE54340.remapped.final.pcl', 'GSE54527.remapped.final.pcl', 'GSE54528.remapped.final.pcl', 'GSE54539.remapped.final.pcl', 'GSE54741.remapped.final.pcl',
# 'GSE55081.remapped.final.pcl', 'GSE55121.remapped.final.pcl', 'GSE55372.remapped.final.pcl', 'GSE56124.remapped.final.pcl', 'GSE56773.remapped.final.pcl'
# ])
#
#     nex_session.close()
#     for path in os.listdir('src/sgd/convert/data/microarray_05_14'):
#         if os.path.isdir('src/sgd/convert/data/microarray_05_14/' + path):
#             for file in os.listdir('src/sgd/convert/data/microarray_05_14/' + path):
#                 if file in new_pcl_files:
#                     dataset_key = (file[:-4], 'DATASET')
#
#                     do_conversion(make_expression_data_starter(nex_session_maker, 'src/sgd/convert/data/microarray_05_14/' + path + '/' + file, dataset_key_to_id[dataset_key], dataset_key_to_channel_count[dataset_key], key_to_locus, aliases),
#                                           [Json2Obj(Bioentitydata),
#                                            Obj2NexDB(nex_session_maker, lambda x: x.query(Bioentitydata).filter(Bioentitydata.evidence_id.in_([datasetcolumn_id_to_evidence_id[y] for y in dataset_id_to_columns[dataset_key_to_id[dataset_key]]])),
#                                                      name='convert.from_bud.evidence.expression_data',
#                                                      delete_untouched=True,
#                                                      commit_interval=1000)])

    # do_conversion(make_bioentity_expression_interaction_starter(nex_session_maker),
    #               [Json2Obj(Bioentityinteraction),
    #                BigObj2NexDB(nex_session_maker, lambda x: x.query(Bioentityinteraction).filter_by(interaction_type='EXPRESSION'),
    #                             name='convert.from_bud.auxilliary.bioentity_interaction_expression',
    #                             delete_untouched=True,
    #                             commit_interval=1000)])
    #
    # # ------------------------------------------ Perf ------------------------------------------
    #
    from src.sgd.model.perf.bioentity_data import BioentityGraph, BioentityDetails

    from src.sgd.model.nex.bioentity import Locus
    nex_session = nex_session_maker()
    locus_ids = [x.id for x in nex_session.query(Locus).all()]
    nex_session.close()
    #
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'expression_graph', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'EXPRESSION', locus_ids,
    #                                 name='convert.from_backend.expression_graph',
    #                                 commit_interval=1000)])
    #
    do_conversion(make_locus_data_backend_starter(nex_backend, 'expression_details', locus_ids),
                   [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'EXPRESSION', locus_ids,
                                    name='convert.from_backend.expression_details',
                                    commit_interval=100)])


    # # ------------------------------------------ Perf2 ------------------------------------------
    # perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    # perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)
    #
    # do_conversion(make_locus_data_backend_starter(perf_backend, 'expression_graph', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityGraph, 'EXPRESSION', locus_ids,
    #                                 name='convert.from_backend.expression_graph',
    #                                 commit_interval=1000)])
    #
    # do_conversion(make_locus_data_backend_starter(perf_backend, 'expression_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'EXPRESSION', locus_ids,
    #                                 name='convert.from_backend.expression_details',
    #                                 commit_interval=100)])