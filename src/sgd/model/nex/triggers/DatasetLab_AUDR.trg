CREATE OR REPLACE TRIGGER DatasetLab_AUDR
--
--  After a row in the dataset_lab table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dataset_lab
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dataset_id != :new.dataset_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_LAB', 'DATASET_ID', :old.dataset_lab_id, :old.dataset_id, :new.dataset_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_LAB', 'SOURCE_ID', :old.dataset_lab_id, :old.source_id, :new.source_id, USER);
    END IF;

     IF (:old.lab_name != :new.lab_name)
    THEN
        AuditLog.InsertUpdateLog('DATASET_LAB', 'LAB_NAME', :old.dataset_lab_id, :old.lab_name, :new.lab_name, USER);
    END IF;

     IF (:old.lab_location != :new.lab_location)
    THEN
        AuditLog.InsertUpdateLog('DATASET_LAB', 'LAB_LOCATION', :old.dataset_lab_id, :old.lab_location, :new.lab_location, USER);
    END IF;

    IF (((:old.colleague_id IS NULL) AND (:new.colleague_id IS NOT NULL)) OR ((:old.colleague_id IS NOT NULL) AND (:new.colleague_id IS NULL)) OR (:old.colleague_id != :new.colleague_id))
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'COLLEAGUE_ID', :old.dataset_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

  ELSE

    v_row := :old.dataset_lab_id || '[:]' || :old.dataset_id || '[:]' ||
             :old.source_id || '[:]' ||  :old.lab_name || '[:]' || 
             :old.lab_location || '[:]' || :old.colleague_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DATASET_LAB', :old.dataset_lab_id, v_row, USER);

  END IF;

END DatasetLab_AUDR;
/
SHOW ERROR
