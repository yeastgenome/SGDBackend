CREATE OR REPLACE TRIGGER Dnasubsequence_AUDR
--
--  After a row in the dnasubsequence table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dnasubsequence
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'ANNOTATION_ID', :old.dnasubsequence_id, :old.annotation_id, :new.annotation_id, USER);
    END IF;

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'DBENTITY_ID', :old.dnasubsequence_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'DISPLAY_NAME', :old.dnasubsequence_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'BUD_ID', :old.dnasubsequence_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.so_id != :new.so_id)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'SO_ID', :old.dnasubsequence_id, :old.so_id, :new.so_id, USER);
    END IF;

    IF (:old.relative_start_index != :new.relative_start_index)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'RELATIVE_START_INDEX', :old.dnasubsequence_id, :old.relative_start_index, :new.relative_start_index, USER);
    END IF;

    IF (:old.relative_end_index != :new.relative_end_index)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'RELATIVE_END_INDEX', :old.dnasubsequence_id, :old.relative_end_index, :new.relative_end_index, USER);
    END IF;

    IF (:old.contig_start_index != :new.contig_start_index)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'CONTIG_START_INDEX', :old.dnasubsequence_id, :old.contig_start_index, :new.contig_start_index, USER);
    END IF;

    IF (:old.contig_end_index != :new.contig_end_index)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'CONTIG_END_INDEX', :old.dnasubsequence_id, :old.contig_end_index, :new.contig_end_index, USER);
    END IF;

    IF (((:old.seq_version IS NULL) AND (:new.seq_version IS NOT NULL)) OR ((:old.seq_version IS NOT NULL) AND (:new.seq_version IS NULL)) OR (:old.seq_version != :new.seq_version))
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'SEQ_VERSION', :old.dnasubsequence_id, :old.seq_version, :new.seq_version, USER);
    END IF;

    IF (((:old.coord_version IS NULL) AND (:new.coord_version IS NOT NULL)) OR ((:old.coord_version IS NOT NULL) AND (:new.coord_version IS NULL)) OR (:old.coord_version != :new.coord_version))
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'COORD_VERSION', :old.dnasubsequence_id, :old.coord_version, :new.coord_version, USER);
    END IF;

    IF (((:old.genomerelease_id IS NULL) AND (:new.genomerelease_id IS NOT NULL)) OR ((:old.genomerelease_id IS NOT NULL) AND (:new.genomerelease_id IS NULL)) OR (:old.genomerelease_id != :new.genomerelease_id))
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'GENOMERELEASE_ID', :old.dnasubsequence_id, :old.genomerelease_id, :new.genomerelease_id, USER);
    END IF;

    IF (:old.file_header != :new.file_header)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'FILE_HEADER', :old.dnasubsequence_id, :old.file_header, :new.file_header, USER);
    END IF;

    IF (:old.download_filename != :new.download_filename)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'DOWNLOAD_FILENAME', :old.dnasubsequence_id, :old.download_filename, :new.download_filename, USER);
    END IF;

    IF (((:old.file_id IS NULL) AND (:new.file_id IS NOT NULL)) OR ((:old.file_id IS NOT NULL) AND (:new.file_id IS NULL)) OR (:old.file_id != :new.file_id))
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'FILE_ID', :old.dnasubsequence_id, :old.file_id, :new.file_id, USER);
    END IF;

     IF (:old.residues != :new.residues)
    THEN
        AuditLog.InsertUpdateLog('DNASUBSEQUENCE', 'RESIDUES', :old.dnasubsequence_id, :old.residues, :new.residues, USER);
    END IF;

  ELSE

    v_row := :old.dnasubsequence_id || '[:]' || :old.annotation_id || '[:]' ||
             :old.dbentity_id || '[:]' || :old.display_name || '[:]' ||
             :old.bud_id || '[:]' || :old.so_id || '[:]' ||
             :old.relative_start_index || '[:]' || :old.relative_end_index || '[:]' ||
             :old.contig_start_index || '[:]' || :old.contig_end_index || '[:]' ||
             :old.seq_version || '[:]' || :old.coord_version || '[:]' ||
             :old.genomerelease_id || '[:]' || :old.file_header || '[:]' ||
             :old.download_filename || '[:]' ||
             :old.file_id || '[:]' || :old.residues || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DNASUBSEQUENCE', :old.dnasubsequence_id, v_row, USER);

  END IF;

END Dnasubsequence_AUDR;
/
SHOW ERROR
