CREATE OR REPLACE TRIGGER Edam_AUDR
--
--  After a row in the edam table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON edam
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('EDAM', 'FORMAT_NAME', :old.edam_id, :old.format_name, :new.format_name, USER);
    END IF;

     IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('EDAM', 'DISPLAY_NAME', :old.edam_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('EDAM', 'OBJ_URL', :old.edam_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('EDAM', 'SOURCE_ID', :old.edam_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('EDAM', 'BUD_ID', :old.edam_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.edamid != :new.edamid)
    THEN
        AuditLog.InsertUpdateLog('EDAM', 'EDAMID', :old.edam_id, :old.edamid, :new.edamid, USER);
    END IF;

     IF (:old.edam_namespace != :new.edam_namespace)
    THEN
        AuditLog.InsertUpdateLog('EDAM', 'EDAM_NAMESPACE', :old.edam_id, :old.edam_namespace, :new.edam_namespace, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('EDAM', 'DESCRIPTION', :old.edam_id, :old.description, :new.description, USER);
    END IF;

  ELSE

    v_row := :old.edam_id || '[:]' || :old.format_name || '[:]' ||  
             :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.edamid || '[:]' || :old.edam_namespace || '[:]' ||
             :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('EDAM', :old.edam_id, v_row, USER);

  END IF;

END Edam_AUDR;
/
SHOW ERROR
