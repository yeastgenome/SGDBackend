CREATE OR REPLACE TRIGGER Proteindomain_AUDR
--
--  After a row in the proteindomain table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON proteindomain
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAIN', 'FORMAT_NAME', :old.proteindomain_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAIN', 'DISPLAY_NAME', :old.proteindomain_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAIN', 'OBJ_URL', :old.proteindomain_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAIN', 'SOURCE_ID', :old.proteindomain_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAIN', 'BUD_ID', :old.proteindomain_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (((:old.interpro_id IS NULL) AND (:new.interpro_id IS NOT NULL)) OR ((:old.interpro_id IS NOT NULL) AND (:new.interpro_id IS NULL)) OR (:old.interpro_id != :new.interpro_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAIN', 'INTERPRO_ID', :old.proteindomain_id, :old.interpro_id, :new.interpro_id, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('PROTEINDOMAIN', 'DESCRIPTION', :old.proteindomain_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.proteindomain_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.interpro_id || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PROTEINDOMAIN', :old.proteindomain_id, v_row, USER);

  END IF;

END Proteindomain_AUDR;
/
SHOW ERROR
