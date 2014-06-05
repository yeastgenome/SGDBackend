from src.sgd.model import nex, perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, OutputTransformer, make_file_starter, \
    Json2DataPerfDB, make_locus_data_backend_starter, make_contig_data_backend_starter

__author__ = 'kpaskov'

if __name__ == "__main__":

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # # ------------------------------------------ Evidence ------------------------------------------
    # from src.sgd.model.nex.evidence import Evidence, DNAsequenceevidence, DNAsequencetag, Proteinsequenceevidence
    # from src.sgd.convert.from_bud.evidence import make_dna_sequence_evidence_starter, make_protein_sequence_evidence_starter, make_dna_sequence_tag_starter
    # from src.sgd.convert.from_bud import sequence_files, protein_sequence_files
    # from src.sgd.model.nex.misc import Strain
    # nex_session = nex_session_maker()
    # strain_key_to_id = dict([(x.unique_key(), x.id) for x in nex_session.query(Strain).all()])
    # nex_session.close()
    #
    # from src.sgd.convert.from_bud import sequence_files, protein_sequence_files
    # from src.sgd.model.nex.misc import Strain
    # nex_session = nex_session_maker()
    # strain_key_to_id = dict([(x.unique_key(), x.id) for x in nex_session.query(Strain).all()])
    # nex_session.close()
    # #
    # for sequence_filename, coding_sequence_filename, strain_key in sequence_files:
    #     do_conversion(make_dna_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, coding_sequence_filename),
    #                   [Json2Obj(DNAsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.strain_id == strain_key_to_id[strain_key]), name='convert.from_bud.evidence.dnasequence', delete_untouched=True, commit_interval=1000),
    #                    OutputTransformer(1000)])
    #
    #     if strain_key == 'S288C':
    #         do_conversion(make_dna_sequence_tag_starter(nex_session_maker, strain_key, sequence_filename),
    #                       [Json2Obj(DNAsequencetag),
    #                        Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequencetag), name='convert.from_bud.evidence.dnasequence.tags', delete_untouched=True, commit_interval=1000),
    #                        OutputTransformer(1000)])
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

    # ------------------------------------------ Perf ------------------------------------------
    from src.sgd.model.perf.bioentity_data import BioentityDetails
    from src.sgd.model.perf.bioitem_data import BioitemDetails

    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioitem import Contig
    nex_session = nex_session_maker()
    #locus_ids = [x.id for x in nex_session.query(Locus).all()]
    contig_ids = [x.id for x in nex_session.query(Contig).all()]
    nex_session.close()

    # do_conversion(make_locus_data_backend_starter(nex_backend, 'neighbor_sequence_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'NEIGHBOR_SEQUENCE', locus_ids, name='convert.from_backend.neighbor_sequence_details', commit_interval=1000),
    #                 OutputTransformer(1000)])
    #
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'sequence_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'SEQUENCE', locus_ids, name='convert.from_backend.sequence_details', commit_interval=1000),
    #                 OutputTransformer(1000)])

    do_conversion(make_contig_data_backend_starter(nex_backend, 'sequence_details', contig_ids),
                   [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'SEQUENCE', contig_ids, name='convert.from_backend.sequence_details', commit_interval=1000),
                    OutputTransformer(1000)])