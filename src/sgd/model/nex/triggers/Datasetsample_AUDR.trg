CREATE OR REPLACE TRIGGER Datasetsample_AUDR
--
--  After a row in the datasetsample table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON datasetsample
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'FORMAT_NAME', :old.datasetsample_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'DISPLAY_NAME', :old.datasetsample_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'OBJ_URL', :old.datasetsample_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'SOURCE_ID', :old.datasetsample_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'BUD_ID', :old.datasetsample_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.dataset_id != :new.dataset_id)
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'DATASET_ID', :old.datasetsample_id, :old.dataset_id, :new.dataset_id, USER);
    END IF;

    IF (:old.sample_order != :new.sample_order)
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'SAMPLE_ORDER', :old.datasetsample_id, :old.sample_order, :new.sample_order, USER);
    END IF;

    IF (((:old.dbxref_id IS NULL) AND (:new.dbxref_id IS NOT NULL)) OR ((:old.dbxref_id IS NOT NULL) AND (:new.dbxref_id IS NULL)) OR (:old.dbxref_id != :new.dbxref_id))
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'DBXREF_ID', :old.datasetsample_id, :old.dbxref_id, :new.dbxref_id, USER);
    END IF;

    IF (((:old.dbxref_type IS NULL) AND (:new.dbxref_type IS NOT NULL)) OR ((:old.dbxref_type IS NOT NULL) AND (:new.dbxref_type IS NULL)) OR (:old.dbxref_type != :new.dbxref_type))
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'DBXREF_TYPE', :old.datasetsample_id, :old.dbxref_type, :new.dbxref_type, USER);
    END IF;

    IF (((:old.biosample IS NULL) AND (:new.biosample IS NOT NULL)) OR ((:old.biosample IS NOT NULL) AND (:new.biosample IS NULL)) OR (:old.biosample != :new.biosample))
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'BIOSAMPLE', :old.datasetsample_id, :old.biosample, :new.biosample, USER);
    END IF;

    IF (((:old.strain_name IS NULL) AND (:new.strain_name IS NOT NULL)) OR ((:old.strain_name IS NOT NULL) AND (:new.strain_name IS NULL)) OR (:old.strain_name != :new.strain_name))
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'STRAIN_NAME', :old.datasetsample_id, :old.strain_name, :new.strain_name, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('DATASETSAMPLE', 'DESCRIPTION', :old.datasetsample_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.datasetsample_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.dataset_id || '[:]' || :old.sample_order || '[:]' ||
             :old.dbxref_id || '[:]' || :old.dbxref_type || '[:]' ||
             :old.biosample || '[:]' || :old.strain_name || '[:]' || 
             :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DATASETSAMPLE', :old.datasetsample_id, v_row, USER);

  END IF;

END Datasetsample_AUDR;
/
SHOW ERROR
