CREATE OR REPLACE TRIGGER Datasetlab_AUDR
--
--  After a row in the datasetlab table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON datasetlab
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dataset_id != :new.dataset_id)
    THEN
        AuditLog.InsertUpdateLog('DATASETLAB', 'DATASET_ID', :old.datasetlab_id, :old.dataset_id, :new.dataset_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DATASETLAB', 'SOURCE_ID', :old.datasetlab_id, :old.source_id, :new.source_id, USER);
    END IF;

     IF (:old.lab_name != :new.lab_name)
    THEN
        AuditLog.InsertUpdateLog('DATASETLAB', 'LAB_NAME', :old.datasetlab_id, :old.lab_name, :new.lab_name, USER);
    END IF;

     IF (:old.lab_location != :new.lab_location)
    THEN
        AuditLog.InsertUpdateLog('DATASETLAB', 'LAB_LOCATION', :old.datasetlab_id, :old.lab_location, :new.lab_location, USER);
    END IF;

    IF (((:old.colleague_id IS NULL) AND (:new.colleague_id IS NOT NULL)) OR ((:old.colleague_id IS NOT NULL) AND (:new.colleague_id IS NULL)) OR (:old.colleague_id != :new.colleague_id))
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'COLLEAGUE_ID', :old.dataset_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

  ELSE

    v_row := :old.datasetlab_id || '[:]' || :old.dataset_id || '[:]' ||
             :old.source_id || '[:]' ||  :old.lab_name || '[:]' || 
             :old.lab_location || '[:]' || :old.colleague_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DATASETLAB', :old.datasetlab_id, v_row, USER);

  END IF;

END Datasetlab_AUDR;
/
SHOW ERROR
