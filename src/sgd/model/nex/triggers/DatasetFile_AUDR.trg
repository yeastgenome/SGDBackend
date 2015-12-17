CREATE OR REPLACE TRIGGER DatasetFile_AUDR
--
--  After a row in the dataset_file table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dataset_file
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.file_id != :new.file_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_FILE', 'FILE_ID', :old.dataset_file_id, :old.file_id, :new.file_id, USER);
    END IF;

     IF (:old.dataset_id != :new.dataset_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_FILE', 'DATASET_ID', :old.dataset_file_id, :old.dataset_id, :new.dataset_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_FILE', 'SOURCE_ID', :old.dataset_file_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.dataset_file_id || '[:]' || :old.file_id || '[:]' ||
             :old.dataset_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DATASET_FILE', :old.dataset_file_id, v_row, USER);

  END IF;

END DatasetFile_AUDR;
/
SHOW ERROR
