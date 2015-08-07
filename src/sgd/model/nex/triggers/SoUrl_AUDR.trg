CREATE OR REPLACE TRIGGER SoUrl_AUDR
--
--  After a row in the so_url table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON so_url
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('SO_URL', 'DISPLAY_NAME', :old.url_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('SO_URL', 'OBJ_URL', :old.url_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('SO_URL', 'SOURCE_ID', :old.url_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('SO_URL', 'BUD_ID', :old.url_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.so_id != :new.so_id)
    THEN
        AuditLog.InsertUpdateLog('SO_URL', 'SO_ID', :old.url_id, :old.so_id, :new.so_id, USER);
    END IF;

    IF (:old.url_type != :new.url_type)
    THEN
        AuditLog.InsertUpdateLog('SO_URL', 'URL_TYPE', :old.url_id, :old.url_type, :new.url_type, USER);
    END IF;

  ELSE

    v_row := :old.url_id || '[:]' || 
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.so_id || '[:]' || :old.url_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('SO_URL', :old.url_id, v_row, USER);

  END IF;

END SoUrl_AUDR;
/
SHOW ERROR
