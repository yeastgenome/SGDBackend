CREATE OR REPLACE TRIGGER Psimod_AUDR
--
--  After a row in the psimod table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON psimod
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('PSIMOD', 'FORMAT_NAME', :old.psimod_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('PSIMOD', 'DISPLAY_NAME', :old.psimod_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('PSIMOD', 'OBJ_URL', :old.psimod_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PSIMOD', 'SOURCE_ID', :old.psimod_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PSIMOD', 'BUD_ID', :old.psimod_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.psimodid != :new.psimodid)
    THEN
        AuditLog.InsertUpdateLog('PSIMOD', 'PSIMODID', :old.psimod_id, :old.psimodid, :new.psimodid, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('PSIMOD', 'DESCRIPTION', :old.psimod_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.psimod_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.psimodid || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PSIMOD', :old.psimod_id, v_row, USER);

  END IF;

END Psimod_AUDR;
/
SHOW ERROR
