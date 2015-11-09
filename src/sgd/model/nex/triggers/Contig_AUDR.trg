CREATE OR REPLACE TRIGGER Contig_AUDR
--
--  After a row in the contig table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON contig
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'FORMAT_NAME', :old.contig_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'DISPLAY_NAME', :old.contig_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'OBJ_URL', :old.contig_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'SOURCE_ID', :old.contig_id, :old.source_id, :new.source_id, USER);
    END IF;

     IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'TAXONOMY_ID', :old.contig_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'BUD_ID', :old.contig_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.so_id != :new.so_id)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'SO_ID', :old.contig_id, :old.so_id, :new.so_id, USER);
    END IF;

    IF (((:old.centromere_start IS NULL) AND (:new.centromere_start IS NOT NULL)) OR ((:old.centromere_start IS NOT NULL) AND (:new.centromere_start IS NULL)) OR (:old.centromere_start != :new.centromere_start))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'CENTROMERE_START', :old.contig_id, :old.centromere_start, :new.centromere_start, USER);
    END IF;

    IF (((:old.centromere_end IS NULL) AND (:new.centromere_end IS NOT NULL)) OR ((:old.centromere_end IS NOT NULL) AND (:new.centromere_end IS NULL)) OR (:old.centromere_end != :new.centromere_end))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'CENTROMERE_END', :old.contig_id, :old.centromere_end, :new.centromere_end, USER);
    END IF;

    IF (:old.genbank_accession != :new.genbank_accession)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'GENBANK_ACCESSION', :old.contig_id, :old.genbank_accession, :new.genbank_accession, USER);
    END IF;

    IF (((:old.gi_number IS NULL) AND (:new.gi_number IS NOT NULL)) OR ((:old.gi_number IS NOT NULL) AND (:new.gi_number IS NULL)) OR (:old.gi_number != :new.gi_number))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'GI_NUMBER', :old.contig_id, :old.gi_number, :new.gi_number, USER);
    END IF;

    IF (((:old.refseq_id IS NULL) AND (:new.refseq_id IS NOT NULL)) OR ((:old.refseq_id IS NOT NULL) AND (:new.refseq_id IS NULL)) OR (:old.refseq_id != :new.refseq_id))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'REFSEQ_ID', :old.contig_id, :old.refseq_id, :new.refseq_id, USER);
    END IF;

    IF (((:old.reference_chromosome_id IS NULL) AND (:new.reference_chromosome_id IS NOT NULL)) OR ((:old.reference_chromosome_id IS NOT NULL) AND (:new.reference_chromosome_id IS NULL)) OR (:old.reference_chromosome_id != :new.reference_chromosome_id))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'REFERENCE_CHROMOSOME_ID', :old.contig_id, :old.reference_chromosome_id, :new.reference_chromosome_id, USER);
    END IF;

    IF (((:old.reference_start IS NULL) AND (:new.reference_start IS NOT NULL)) OR ((:old.reference_start IS NOT NULL) AND (:new.reference_start IS NULL)) OR (:old.reference_start != :new.reference_start))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'REFERENCE_START', :old.contig_id, :old.reference_start, :new.reference_start, USER);
    END IF;

    IF (((:old.reference_end IS NULL) AND (:new.reference_end IS NOT NULL)) OR ((:old.reference_end IS NOT NULL) AND (:new.reference_end IS NULL)) OR (:old.reference_end != :new.reference_end))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'REFERENCE_END', :old.contig_id, :old.reference_end, :new.reference_end, USER);
    END IF;

    IF (((:old.reference_percent_identity IS NULL) AND (:new.reference_percent_identity IS NOT NULL)) OR ((:old.reference_percent_identity IS NOT NULL) AND (:new.reference_percent_identity IS NULL)) OR (:old.reference_percent_identity != :new.reference_percent_identity))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'REFERENCE_PERCENT_IDENTITY', :old.contig_id, :old.reference_percent_identity, :new.reference_percent_identity, USER);
    END IF;

    IF (((:old.reference_alignment_length IS NULL) AND (:new.reference_alignment_length IS NOT NULL)) OR ((:old.reference_alignment_length IS NOT NULL) AND (:new.reference_alignment_length IS NULL)) OR (:old.reference_alignment_length != :new.reference_alignment_length))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'REFERENCE_ALIGNMENT_LENGTH', :old.contig_id, :old.reference_alignment_length, :new.reference_alignment_length, USER);
    END IF;

    IF (((:old.seq_version IS NULL) AND (:new.seq_version IS NOT NULL)) OR ((:old.seq_version IS NOT NULL) AND (:new.seq_version IS NULL)) OR (:old.seq_version != :new.seq_version))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'SEQ_VERSION', :old.contig_id, :old.seq_version, :new.seq_version, USER);
    END IF;

    IF (((:old.coord_version IS NULL) AND (:new.coord_version IS NOT NULL)) OR ((:old.coord_version IS NOT NULL) AND (:new.coord_version IS NULL)) OR (:old.coord_version != :new.coord_version))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'COORD_VERSION', :old.contig_id, :old.coord_version, :new.coord_version, USER);
    END IF;

    IF (((:old.genomerelease_id IS NULL) AND (:new.genomerelease_id IS NOT NULL)) OR ((:old.genomerelease_id IS NOT NULL) AND (:new.genomerelease_id IS NULL)) OR (:old.genomerelease_id != :new.genomerelease_id))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'GENOMERELEASE_ID', :old.contig_id, :old.genomerelease_id, :new.genomerelease_id, USER);
    END IF;

    IF (:old.file_header != :new.file_header)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'FILE_HEADER', :old.contig_id, :old.file_header, :new.file_header, USER);
    END IF;

    IF (:old.download_filename != :new.download_filename)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'DOWNLOAD_FILENAME', :old.contig_id, :old.download_filename, :new.download_filename, USER);
    END IF;

    IF (((:old.file_id IS NULL) AND (:new.file_id IS NOT NULL)) OR ((:old.file_id IS NOT NULL) AND (:new.file_id IS NULL)) OR (:old.file_id != :new.file_id))
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'FILE_ID', :old.contig_id, :old.file_id, :new.file_id, USER);
    END IF;

     IF (:old.residues != :new.residues)
    THEN
        AuditLog.InsertUpdateLog('CONTIG', 'RESIDUES', :old.contig_id, :old.residues, :new.residues, USER);
    END IF;

  ELSE

    v_row := :old.contig_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.taxonomy_id || '[:]' || :old.so_id || '[:]' ||
             :old.centromere_start || '[:]' || :old.centromere_end || '[:]' ||
             :old.genbank_accession || '[:]' || :old.gi_number || '[:]' ||
             :old.refseq_id || '[:]' || :old.reference_chromosome_id || '[:]' ||
             :old.reference_start || '[:]' || :old.reference_end || '[:]' ||
             :old.reference_percent_identity || '[:]' || :old.reference_alignment_length || '[:]' ||
             :old.seq_version || '[:]' || :old.coord_version || '[:]' ||
             :old.genomerelease_id || '[:]' || :old.file_header || '[:]' ||
             :old.download_filename || '[:]' ||
             :old.file_id || '[:]' || :old.residues || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('CONTIG', :old.contig_id, v_row, USER);

  END IF;

END Contig_AUDR;
/
SHOW ERROR
