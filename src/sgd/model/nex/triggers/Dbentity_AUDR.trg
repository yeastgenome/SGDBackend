CREATE OR REPLACE TRIGGER Dbentity_AUDR
--
--  After a row in the dbentity table is updated, or deleted 
--  execute a trigger to write a record to the sgdid, update_log, or delete_log tables
--  USE ONLY FOR INITIAL DATA LOAD WHEN SGDIDs ARE PRE-LOADED!
--
    AFTER UPDATE OR DELETE ON dbentity
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('DBENTITY', 'FORMAT_NAME', :old.dbentity_id, :old.format_name, :new.format_name, USER);
    END IF;

    IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('DBENTITY', 'DISPLAY_NAME', :old.dbentity_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('DBENTITY', 'OBJ_URL', :old.dbentity_id, :old.obj_url, :new.obj_url, USER);
    END IF;

    IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DBENTITY', 'SOURCE_ID', :old.dbentity_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('DBENTITY', 'BUD_ID', :old.dbentity_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.sgdid != :new.sgdid)
    THEN
        AuditLog.InsertUpdateLog('DBENTITY', 'SGDID', :old.dbentity_id, :old.sgdid, :new.sgdid, USER);
    END IF;

    IF (:old.subclass != :new.subclass)
    THEN
        AuditLog.InsertUpdateLog('DBENTITY', 'SUBCLASS', :old.dbentity_id, :old.subclass, :new.subclass, USER);
    END IF;

    IF (:old.dbentity_status != :new.dbentity_status)
    THEN
        AuditLog.InsertUpdateLog('DBENTITY', 'DBENTITY_STATUS', :old.dbentity_id, :old.dbentity_status, :new.dbentity_status, USER);
--		InsertHistory.InsertHistory(:old.dbentity_id, 'SGD', SYSDATE, 'DBENTITY', 'Dbentity status', :old.dbentity_status, :new.dbentity_status, 'Dbentity status change', USER);
    END IF;

  ELSE

    UPDATE sgdid SET sgdid_status = 'Deleted'
    WHERE display_name = :old.sgdid;

    v_row := :old.dbentity_id || '[:]' || :old.format_name || '[:]' || 
             :old.display_name || '[:]' || :old.obj_url || '[:]' || 
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.sgdid || '[:]' || :old.subclass || '[:]' ||
             :old.dbentity_status || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DBENTITY', :old.dbentity_id, v_row, USER);

  END IF;

END Dbentity_AUDR;
/
SHOW ERROR
