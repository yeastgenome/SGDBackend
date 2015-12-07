CREATE OR REPLACE TRIGGER Dnasequenceannotation_AUDR
--
--  After a row in the dnasequenceannotation table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dnasequenceannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
    v_part       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

     IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

     IF (:old.so_id != :new.so_id)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'SO_ID', :old.annotation_id, :old.so_id, :new.so_id, USER);
    END IF;

    IF (:old.dna_type != :new.dna_type)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'DNA_TYPE', :old.annotation_id, :old.dna_type, :new.dna_type, USER);
    END IF;

    IF (:old.contig_id != :new.contig_id)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'CONTIG_ID', :old.annotation_id, :old.contig_id, :new.contig_id, USER);
    END IF;

    IF (((:old.seq_version IS NULL) AND (:new.seq_version IS NOT NULL)) OR ((:old.seq_version IS NOT NULL) AND (:new.seq_version IS NULL)) OR (:old.seq_version != :new.seq_version))
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'SEQ_VERSION', :old.annotation_id, :old.seq_version, :new.seq_version, USER);
    END IF;

    IF (((:old.coord_version IS NULL) AND (:new.coord_version IS NOT NULL)) OR ((:old.coord_version IS NOT NULL) AND (:new.coord_version IS NULL)) OR (:old.coord_version != :new.coord_version))
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'COORD_VERSION', :old.annotation_id, :old.coord_version, :new.coord_version, USER);
    END IF;

    IF (((:old.genomerelease_id IS NULL) AND (:new.genomerelease_id IS NOT NULL)) OR ((:old.genomerelease_id IS NOT NULL) AND (:new.genomerelease_id IS NULL)) OR (:old.genomerelease_id != :new.genomerelease_id))
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'GENOMERELEASE_ID', :old.annotation_id, :old.genomerelease_id, :new.genomerelease_id, USER);
    END IF;

    IF (:old.start_index != :new.start_index)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'START_INDEX', :old.annotation_id, :old.start_index, :new.start_index, USER);
    END IF;

    IF (:old.end_index != :new.end_index)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'END_INDEX', :old.annotation_id, :old.end_index, :new.end_index, USER);
    END IF;

    IF (:old.strand != :new.strand)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'STRAND', :old.annotation_id, :old.strand, :new.strand, USER);
    END IF;

    IF (:old.file_header != :new.file_header)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'FILE_HEADER', :old.annotation_id, :old.file_header, :new.file_header, USER);
    END IF;

    IF (:old.download_filename != :new.download_filename)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'DOWNLOAD_FILENAME', :old.annotation_id, :old.download_filename, :new.download_filename, USER);
    END IF;

    IF (((:old.file_id IS NULL) AND (:new.file_id IS NOT NULL)) OR ((:old.file_id IS NOT NULL) AND (:new.file_id IS NULL)) OR (:old.file_id != :new.file_id))
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'FILE_ID', :old.annotation_id, :old.file_id, :new.file_id, USER);
    END IF;

     IF (:old.residues != :new.residues)
    THEN
        AuditLog.InsertUpdateLog('DNASEQUENCEANNOTATION', 'RESIDUES', :old.annotation_id, :old.residues, :new.residues, USER);
    END IF;

  ELSE

    v_part := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' ||
             :old.reference_id || '[:]' || :old.bud_id || '[:]' ||
             :old.so_id || '[:]' || :old.dna_type || '[:]' || 
             :old.contig_id || '[:]' || :old.seq_version || '[:]' || 
             :old.coord_version || '[:]' || :old.genomerelease_id || '[:]' || 
             :old.start_index || '[:]' || :old.end_index || '[:]' ||
             :old.strand || '[:]' || :old.file_header || '[:]' || 
             :old.download_filename || '[:]' || :old.file_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    v_row := concat(concat(v_part, '[:]'), :old.residues);

    AuditLog.InsertDeleteLog('DNASEQUENCEANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Dnasequenceannotation_AUDR;
/
SHOW ERROR
