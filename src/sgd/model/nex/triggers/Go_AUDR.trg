CREATE OR REPLACE TRIGGER Go_AUDR
--
--  After a row in the go table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON go
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('GO', 'FORMAT_NAME', :old.go_id, :old.format_name, :new.format_name, USER);
    END IF;

     IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('GO', 'DISPLAY_NAME', :old.go_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('GO', 'OBJ_URL', :old.go_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('GO', 'SOURCE_ID', :old.go_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('GO', 'BUD_ID', :old.go_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.goid != :new.goid)
    THEN
        AuditLog.InsertUpdateLog('GO', 'GOID', :old.go_id, :old.goid, :new.goid, USER);
    END IF;

     IF (:old.go_namespace != :new.go_namespace)
    THEN
        AuditLog.InsertUpdateLog('GO', 'GO_NAMESPACE', :old.go_id, :old.go_namespace, :new.go_namespace, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('GO', 'DESCRIPTION', :old.go_id, :old.description, :new.description, USER);
    END IF;

  ELSE

    v_row := :old.go_id || '[:]' || :old.format_name || '[:]' ||  
             :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.goid || '[:]' || :old.go_namespace || '[:]' ||
             :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('GO', :old.go_id, v_row, USER);

  END IF;

END Go_AUDR;
/
SHOW ERROR
