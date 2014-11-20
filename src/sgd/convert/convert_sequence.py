from src.sgd.model import nex, perf, bud
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.perf import PerfBackend
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj, make_file_starter, \
    Json2DataPerfDB, make_locus_data_backend_starter, make_contig_data_backend_starter

__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    nex_backend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

    # ------------------------------------------ Evidence ------------------------------------------
    from src.sgd.model.nex.evidence import Evidence, DNAsequenceevidence, DNAsequencetag, Proteinsequenceevidence
    from src.sgd.model.nex.bioitem import Contig, Bioitem, Bioitemurl
    from src.sgd.convert.from_bud.evidence import make_dna_sequence_evidence_starter, make_protein_sequence_evidence_starter, \
        make_dna_sequence_tag_starter, make_ref_dna_sequence_evidence_starter, make_kb_sequence_starter, make_new_dna_sequence_evidence_starter
    from src.sgd.convert.from_bud.bioitem import make_contig_starter, update_contig_centromeres, update_contig_reference_alignment, make_bioitem_url_starter
    from src.sgd.convert.from_bud.evelements import make_strain_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter
    from src.sgd.convert.from_bud import sequence_files, protein_sequence_files, new_sequence_files
    from src.sgd.model.nex.misc import Strain, Url
    from src.sgd.model.nex.auxiliary import Disambig

    # do_conversion(make_strain_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Strain),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Strain),
    #                          name='convert.from_bud.strain',
    #                          delete_untouched=True,
    #                          commit=True)])
    #
    # do_conversion(make_contig_starter(bud_session_maker, nex_session_maker),
    #               [Json2Obj(Contig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Contig),
    #                          name='convert.from_bud.bioitem.contig',
    #                          delete_untouched=True,
    #                          commit=True,
    #                          already_deleted=clean_up_orphans(nex_session_maker, Contig, Bioitem, 'CONTIG'))])
    #
    # do_conversion(make_disambig_starter(nex_session_maker, Contig, ['id', 'format_name'], 'BIOITEM', 'CONTIG'),
    #               [Json2Obj(Disambig),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'BIOITEM').filter(Disambig.subclass_type == 'CONTIG'),
    #                          name='convert.from_bud.bioitem.disambig.contig',
    #                          delete_untouched=True,
    #                          commit=True)])
    #
    # do_conversion(make_bioitem_url_starter(nex_session_maker),
    #               [Json2Obj(Bioitemurl),
    #                Obj2NexDB(nex_session_maker, lambda x: x.query(Bioitemurl),
    #                          name='convert.from_bud.bioitem.url',
    #                          delete_untouched=True,
    #                          commit=True,
    #                          already_deleted=clean_up_orphans(nex_session_maker, Bioitemurl, Url, 'BIOITEM'))])

    do_conversion(make_ref_dna_sequence_evidence_starter(bud_session_maker, nex_session_maker, ["src/sgd/convert/data/strains/orf_coding_all.fasta", "src/sgd/convert/data/strains/rna_coding.fasta"]),
                      [Json2Obj(DNAsequenceevidence),
                       Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.strain_id == 1), name='convert.from_bud.evidence.reference_dnasequence', delete_untouched=True, commit_interval=1000)])

    do_conversion(make_dna_sequence_tag_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(DNAsequencetag),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequencetag), name='convert.from_bud.evidence.dnasequence.tags', delete_untouched=True, commit_interval=1000)])

    # nex_session = nex_session_maker()
    # strain_key_to_id = dict([(x.unique_key(), x.id) for x in nex_session.query(Strain).all()])
    # nex_session.close()
    #
    # for sequence_filename, coding_sequence_filename, strain_key in sequence_files:
    #     do_conversion(make_dna_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, coding_sequence_filename),
    #                   [Json2Obj(DNAsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.strain_id == strain_key_to_id[strain_key]), name='convert.from_bud.evidence.dnasequence', delete_untouched=True, commit_interval=1000)])

    # clean_up_orphans(nex_session_maker, DNAsequenceevidence, Evidence, 'DNASEQUENCE')
    # for sequence_filename, coding_sequence_filename, strain_key in new_sequence_files:
    #     do_conversion(make_new_dna_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, coding_sequence_filename),
    #                   [Json2Obj(DNAsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.strain_id == strain_key_to_id[strain_key]).filter(DNAsequenceevidence.dna_type != '1KB'),
    #                              name='convert.from_bud.evidence.dnasequence',
    #                              delete_untouched=True,
    #                              commit_interval=1000)])


    #update_contig_centromeres(nex_session_maker)
    #update_contig_reference_alignment(nex_session_maker)


    # protparam_data = dict([(row[0], row) for row in make_file_starter('src/sgd/convert/data/ProtParam.txt')()])
    # for sequence_filename, strain_key in protein_sequence_files:
    #     do_conversion(make_protein_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, protparam_data),
    #                   [Json2Obj(Proteinsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(Proteinsequenceevidence).filter(Proteinsequenceevidence.strain_id == strain_key_to_id[strain_key]), name='convert.from_bud.evidence.proteinsequence', delete_untouched=True, commit_interval=1000)])
    # clean_up_orphans(nex_session_maker, Proteinsequenceevidence, Evidence, 'PROTEINSEQUENCE')

    # do_conversion(make_kb_sequence_starter(nex_session_maker),
    #                   [Json2Obj(DNAsequenceevidence),
    #                    Obj2NexDB(nex_session_maker, lambda x: x.query(DNAsequenceevidence).filter(DNAsequenceevidence.dna_type == '1KB'),
    #                              name='convert.from_bud.evidence.1kb_dnasequence',
    #                              delete_untouched=True,
    #                              commit_interval=1000)])



    # ------------------------------------------ Perf ------------------------------------------
    # from src.sgd.model.perf.bioentity_data import BioentityDetails
    # from src.sgd.model.perf.bioitem_data import BioitemDetails
    #
    # from src.sgd.model.nex.bioentity import Locus
    # from src.sgd.model.nex.bioitem import Contig
    #nex_session = nex_session_maker()
    #locus_ids = [x.id for x in nex_session.query(Locus).all()]
    #contig_ids = [x.id for x in nex_session.query(Contig).all()]
    #nex_session.close()

    # do_conversion(make_locus_data_backend_starter(nex_backend, 'neighbor_sequence_details', locus_ids),
    #               [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'NEIGHBOR_SEQUENCE', locus_ids, name='convert.from_backend.neighbor_sequence_details', commit_interval=1000)])
    #
    # locus_ids = [58, 79, 140, 374, 399, 448, 572, 1015, 1236, 2195, 2273, 2515, 2791, 3187, 3292, 3414, 4177, 4706, 4752, 6190, 6543, 6759, 6832, 7023];
    # do_conversion(make_locus_data_backend_starter(nex_backend, 'sequence_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'SEQUENCE', locus_ids, name='convert.from_backend.sequence_details', commit_interval=1000)])

    # do_conversion(make_contig_data_backend_starter(nex_backend, 'sequence_details', contig_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'SEQUENCE', contig_ids, name='convert.from_backend.sequence_details', commit_interval=1000)])

    # # # ------------------------------------------ Perf2 ------------------------------------------
    # perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    # perf_backend = PerfBackend(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, None)
    #
    # do_conversion(make_locus_data_backend_starter(perf_backend, 'neighbor_sequence_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'NEIGHBOR_SEQUENCE', locus_ids, name='convert.from_backend.neighbor_sequence_details', commit_interval=1000)])
    #
    # do_conversion(make_locus_data_backend_starter(perf_backend, 'sequence_details', locus_ids),
    #                [Json2DataPerfDB(perf_session_maker, BioentityDetails, 'SEQUENCE', locus_ids, name='convert.from_backend.sequence_details', commit_interval=1000)])
    #
    # # do_conversion(make_contig_data_backend_starter(perf_backend, 'sequence_details', contig_ids),
    # #                [Json2DataPerfDB(perf_session_maker, BioitemDetails, 'SEQUENCE', contig_ids, name='convert.from_backend.sequence_details', commit_interval=1000)])