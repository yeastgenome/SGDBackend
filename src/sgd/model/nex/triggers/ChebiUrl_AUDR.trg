CREATE OR REPLACE TRIGGER ChebiUrl_AUDR
--
--  After a row in the chebi_url table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON chebi_url
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('CHEBI_URL', 'DISPLAY_NAME', :old.url_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('CHEBI_URL', 'OBJ_URL', :old.url_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('CHEBI_URL', 'SOURCE_ID', :old.url_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('CHEBI_URL', 'BUD_ID', :old.url_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.chebi_id != :new.chebi_id)
    THEN
        AuditLog.InsertUpdateLog('CHEBI_URL', 'CHEBI_ID', :old.url_id, :old.chebi_id, :new.chebi_id, USER);
    END IF;

    IF (:old.url_type != :new.url_type)
    THEN
        AuditLog.InsertUpdateLog('CHEBI_URL', 'URL_TYPE', :old.url_id, :old.url_type, :new.url_type, USER);
    END IF;

  ELSE

    v_row := :old.url_id || '[:]' || 
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.chebi_id || '[:]' || :old.url_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('CHEBI_URL', :old.url_id, v_row, USER);

  END IF;

END ChebiUrl_AUDR;
/
SHOW ERROR
