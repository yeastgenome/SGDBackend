CREATE OR REPLACE TRIGGER Apo_AUDR
--
--  After a row in the apo table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON apo
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('APO', 'FORMAT_NAME', :old.apo_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('APO', 'DISPLAY_NAME', :old.apo_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('APO', 'OBJ_URL', :old.apo_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('APO', 'SOURCE_ID', :old.apo_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('APO', 'BUD_ID', :old.apo_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.apoid != :new.apoid)
    THEN
        AuditLog.InsertUpdateLog('APO', 'APOID', :old.apo_id, :old.apoid, :new.apoid, USER);
    END IF;

    IF (:old.apo_namespace != :new.apo_namespace)
    THEN
        AuditLog.InsertUpdateLog('APO', 'APO_NAMESPACE', :old.apo_id, :old.apo_namespace, :new.apo_namespace, USER);
    END IF;

    IF (((:old.namespace_group IS NULL) AND (:new.namespace_group IS NOT NULL)) OR ((:old.namespace_group IS NOT NULL) AND (:new.namespace_group IS NULL)) OR (:old.namespace_group != :new.namespace_group))
    THEN
        AuditLog.InsertUpdateLog('APO', 'NAMESPACE_GROUP', :old.apo_id, :old.namespace_group, :new.namespace_group, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('APO', 'DESCRIPTION', :old.apo_id, :old.description, :new.description, USER);
    END IF;

  ELSE

    v_row := :old.apo_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.apo_id || '[:]' || :old.apo_namespace || '[:]' ||
             :old.namespace_group || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('APO', :old.apo_id, v_row, USER);

  END IF;

END Apo_AUDR;
/
SHOW ERROR
