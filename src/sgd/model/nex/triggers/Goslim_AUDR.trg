CREATE OR REPLACE TRIGGER Goslim_AUDR
--
--  After a row in the goslim table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON goslim
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'FORMAT_NAME', :old.goslim_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'DISPLAY_NAME', :old.goslim_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'OBJ_URL', :old.goslim_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'SOURCE_ID', :old.goslim_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'BUD_ID', :old.goslim_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.go_id != :new.go_id)
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'GO_ID', :old.goslim_id, :old.go_id, :new.go_id, USER);
    END IF;

     IF (:old.slim_name != :new.slim_name)
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'SLIM_NAME', :old.goslim_id, :old.slim_name, :new.slim_name, USER);
    END IF;

     IF (:old.genome_count != :new.genome_count)
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'GENOME_COUNT', :old.goslim_id, :old.genome_count, :new.genome_count, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('GOSLIM', 'DESCRIPTION', :old.goslim_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.goslim_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.go_id || '[:]' || :old.slim_name || '[:]' ||
             :old.genome_count || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('GOSLIM', :old.goslim_id, v_row, USER);

  END IF;

END Goslim_AUDR;
/
SHOW ERROR
