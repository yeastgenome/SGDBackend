CREATE OR REPLACE TRIGGER Dbxref_AUDR
--
--  After a row in the dbxref table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dbxref
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('DBXREF', 'FORMAT_NAME', :old.dbxref_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('DBXREF', 'DISPLAY_NAME', :old.dbxref_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('DBXREF', 'OBJ_URL', :old.dbxref_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DBXREF', 'SOURCE_ID', :old.dbxref_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('DBXREF', 'BUD_ID', :old.dbxref_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.dbxref_type != :new.dbxref_type)
    THEN
        AuditLog.InsertUpdateLog('DBXREF', 'DBXREF_TYPE', :old.dbxref_id, :old.dbxref_type, :new.dbxref_type, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('DBXREF', 'DESCRIPTION', :old.dbxref_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.dbxref_id || '[:]' || :old.format_name || '[:]' ||
             :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.dbxref_type || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DBXREF', :old.dbxref_id, v_row, USER);

  END IF;

END Dbxref_AUDR;
/
SHOW ERROR
