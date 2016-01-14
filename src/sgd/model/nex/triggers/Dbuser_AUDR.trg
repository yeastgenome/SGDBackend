CREATE OR REPLACE TRIGGER Dbuser_AUDR
--
--  After a dbuser row is updated or deleted, 
--  write the record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dbuser
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.username != :new.username)
    THEN
        AuditLog.InsertUpdateLog('DBUSER', 'USERNAME', :old.dbuser_id, :old.username, :new.username, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id)) 
    THEN
        AuditLog.InsertUpdateLog('DBUSER', 'BUD_ID', :old.dbuser_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.first_name != :new.first_name)
    THEN
        AuditLog.InsertUpdateLog('DBUSER', 'FIRST_NAME', :old.dbuser_id, :old.first_name, :new.first_name, USER);
    END IF;

    IF (:old.last_name != :new.last_name)
    THEN
        AuditLog.InsertUpdateLog('DBUSER', 'LAST_NAME', :old.dbuser_id, :old.last_name, :new.last_name, USER);
    END IF;

    IF (:old.status != :new.status)
    THEN
        AuditLog.InsertUpdateLog('DBUSER', 'STATUS', :old.dbuser_id, :old.status, :new.status, USER);
    END IF;

    IF (:old.is_curator != :new.is_curator)
    THEN
        AuditLog.InsertUpdateLog('DBUSER', 'IS_CURATOR', :old.dbuser_id, :old.is_curator, :new.is_curator, USER);
    END IF;

    IF (:old.email != :new.email)
    THEN
        AuditLog.InsertUpdateLog('DBUSER', 'EMAIL', :old.dbuser_id, :old.email, :new.email, USER);
    END IF;

  ELSE

    v_row := :old.dbuser_id || '[:]' || :old.username || '[:]' ||
		  	 :old.bud_id || '[:]' ||
             :old.first_name || '[:]' || :old.last_name || '[:]' || 
             :old.status || '[:]' || :old.is_curator || '[:]' || 
             :old.email || '[:]' || :old.date_created;

    AuditLog.InsertDeleteLog('DBUSER', :old.dbuser_id, v_row, USER);

  END IF;

END Dbuser_AUDR;
/
SHOW ERROR
