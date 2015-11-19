CREATE OR REPLACE TRIGGER Proteinsequenceannotation_AUDR
--
--  After a row in the proteinsequenceannotation table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON proteinsequenceannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

     IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.contig_id != :new.contig_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'CONTIG_ID', :old.annotation_id, :old.contig_id, :new.contig_id, USER);
    END IF;

    IF (((:old.seq_version IS NULL) AND (:new.seq_version IS NOT NULL)) OR ((:old.seq_version IS NOT NULL) AND (:new.seq_version IS NULL)) OR (:old.seq_version != :new.seq_version))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'SEQ_VERSION', :old.annotation_id, :old.seq_version, :new.seq_version, USER);
    END IF;

    IF (((:old.coord_version IS NULL) AND (:new.coord_version IS NOT NULL)) OR ((:old.coord_version IS NOT NULL) AND (:new.coord_version IS NULL)) OR (:old.coord_version != :new.coord_version))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'COORD_VERSION', :old.annotation_id, :old.coord_version, :new.coord_version, USER);
    END IF;

    IF (((:old.genomerelease_id IS NULL) AND (:new.genomerelease_id IS NOT NULL)) OR ((:old.genomerelease_id IS NOT NULL) AND (:new.genomerelease_id IS NULL)) OR (:old.genomerelease_id != :new.genomerelease_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'GENOMERELEASE_ID', :old.annotation_id, :old.genomerelease_id, :new.genomerelease_id, USER);
    END IF;

    IF (:old.file_header != :new.file_header)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'FILE_HEADER', :old.annotation_id, :old.file_header, :new.file_header, USER);
    END IF;

    IF (:old.download_filename != :new.download_filename)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'DOWNLOAD_FILENAME', :old.annotation_id, :old.download_filename, :new.download_filename, USER);
    END IF;

    IF (((:old.file_id IS NULL) AND (:new.file_id IS NOT NULL)) OR ((:old.file_id IS NOT NULL) AND (:new.file_id IS NULL)) OR (:old.file_id != :new.file_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'FILE_ID', :old.annotation_id, :old.file_id, :new.file_id, USER);
    END IF;

     IF (:old.residues != :new.residues)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCEANNOTATION', 'RESIDUES', :old.annotation_id, :old.residues, :new.residues, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' ||
             :old.reference_id || '[:]' || :old.bud_id || '[:]' ||
             :old.contig_id || '[:]' || :old.seq_version || '[:]' || 
             :old.coord_version || '[:]' || :old.genomerelease_id || '[:]' || 
             :old.file_header || '[:]' || :old.download_filename || '[:]' ||
             :old.file_id || '[:]' || :old.residues || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PROTEINSEQUENCEANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Proteinsequenceannotation_AUDR;
/
SHOW ERROR
