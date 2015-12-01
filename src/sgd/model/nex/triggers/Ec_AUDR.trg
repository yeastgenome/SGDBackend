CREATE OR REPLACE TRIGGER Ec_AUDR
--
--  After a row in the ec table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON ec
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('EC', 'FORMAT_NAME', :old.ec_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('EC', 'DISPLAY_NAME', :old.ec_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('EC', 'OBJ_URL', :old.ec_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('EC', 'SOURCE_ID', :old.ec_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('EC', 'BUD_ID', :old.ec_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.ecid != :new.ecid)
    THEN
        AuditLog.InsertUpdateLog('EC', 'ECID', :old.ec_id, :old.ecid, :new.ecid, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('EC', 'DESCRIPTION', :old.ec_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.ec_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.ecid || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('EC', :old.ec_id, v_row, USER);

  END IF;

END Ec_AUDR;
/
SHOW ERROR
