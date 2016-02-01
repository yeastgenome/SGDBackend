CREATE OR REPLACE TRIGGER ReferenceFile_AUDR
--
--  After a row in the reference_file table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON reference_file
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_FILE', 'REFERENCE_ID', :old.reference_file_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.file_id != :new.file_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_FILE', 'FILE_ID', :old.reference_file_id, :old.file_id, :new.file_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_FILE', 'SOURCE_ID', :old.reference_file_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.reference_file_id || '[:]' || :old.reference_id || '[:]' ||
             :old.file_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('REFERENCE_FILE', :old.reference_file_id, v_row, USER);

  END IF;

END ReferenceFile_AUDR;
/
SHOW ERROR
