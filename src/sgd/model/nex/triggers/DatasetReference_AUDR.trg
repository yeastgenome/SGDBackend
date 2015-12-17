CREATE OR REPLACE TRIGGER DatasetReference_AUDR
--
--  After a row in the dataset_reference table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dataset_reference
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dataset_id != :new.dataset_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_REFERENCE', 'DATASET_ID', :old.dataset_reference_id, :old.dataset_id, :new.dataset_id, USER);
    END IF;

     IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_REFERENCE', 'REFERENCE_ID', :old.dataset_reference_id, :old.reference_id, :new.reference_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_REFERENCE', 'SOURCE_ID', :old.dataset_reference_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.dataset_reference_id || '[:]' || :old.reference_id || '[:]' ||
             :old.dataset_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DATASET_REFERENCE', :old.dataset_reference_id, v_row, USER);

  END IF;

END DatasetReference_AUDR;
/
SHOW ERROR
