CREATE OR REPLACE TRIGGER Datasettrack_AUDR
--
--  After a row in the datasettrack table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON datasettrack
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('DATASETTRACK', 'FORMAT_NAME', :old.datasettrack_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('DATASETTRACK', 'DISPLAY_NAME', :old.datasettrack_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('DATASETTRACK', 'OBJ_URL', :old.datasettrack_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DATASETTRACK', 'SOURCE_ID', :old.datasettrack_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.dataset_id != :new.dataset_id)
    THEN
        AuditLog.InsertUpdateLog('DATASETTRACK', 'DATASET_ID', :old.datasettrack_id, :old.dataset_id, :new.dataset_id, USER);
    END IF;

    IF (:old.track_order != :new.track_order)
    THEN
        AuditLog.InsertUpdateLog('DATASETTRACK', 'TRACK_ORDER', :old.datasettrack_id, :old.track_order, :new.track_order, USER);
    END IF;

    IF (:old.track_file_type != :new.track_file_type)
    THEN
        AuditLog.InsertUpdateLog('DATASETTRACK', 'TRACK_FILE_TYPE', :old.datasettrack_id, :old.track_file_type, :new.track_file_type, USER);
    END IF;

  ELSE

    v_row := :old.datasettrack_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.dataset_id || '[:]' || 
             :old.track_order || '[:]' || :old.track_file_type || '[:]' || 
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DATASETTRACK', :old.datasettrack_id, v_row, USER);

  END IF;

END Datasettrack_AUDR;
/
SHOW ERROR
