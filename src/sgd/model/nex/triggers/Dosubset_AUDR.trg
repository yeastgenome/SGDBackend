CREATE OR REPLACE TRIGGER Dosubset_AUDR
--
--  After a row in the dosubset table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dosubset
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'FORMAT_NAME', :old.dosubset_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'DISPLAY_NAME', :old.dosubset_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'OBJ_URL', :old.dosubset_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'SOURCE_ID', :old.dosubset_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'BUD_ID', :old.dosubset_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.do_id != :new.do_id)
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'DO_ID', :old.dosubset_id, :old.do_id, :new.do_id, USER);
    END IF;

     IF (:old.subset_name != :new.subset_name)
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'SUBSET_NAME', :old.dosubset_id, :old.subset_name, :new.subset_name, USER);
    END IF;

     IF (:old.genome_count != :new.genome_count)
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'GENOME_COUNT', :old.dosubset_id, :old.genome_count, :new.genome_count, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('DOSUBSET', 'DESCRIPTION', :old.dosubset_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.dosubset_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.do_id || '[:]' || :old.subset_name || '[:]' ||
             :old.genome_count || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DOSUBSET', :old.dosubset_id, v_row, USER);

  END IF;

END Dosubset_AUDR;
/
SHOW ERROR
