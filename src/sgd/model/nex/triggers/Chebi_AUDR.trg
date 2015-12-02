CREATE OR REPLACE TRIGGER Chebi_AUDR
--
--  After a row in the chebi table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON chebi
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('CHEBI', 'FORMAT_NAME', :old.chebi_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('CHEBI', 'DISPLAY_NAME', :old.chebi_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('CHEBI', 'OBJ_URL', :old.chebi_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('CHEBI', 'SOURCE_ID', :old.chebi_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('CHEBI', 'BUD_ID', :old.chebi_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.chebiid != :new.chebiid)
    THEN
        AuditLog.InsertUpdateLog('CHEBI', 'CHEBIID', :old.chebi_id, :old.chebiid, :new.chebiid, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('CHEBI', 'DESCRIPTION', :old.chebi_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.chebi_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.chebiid || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('CHEBI', :old.chebi_id, v_row, USER);

  END IF;

END Chebi_AUDR;
/
SHOW ERROR