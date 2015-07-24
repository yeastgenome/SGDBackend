CREATE OR REPLACE TRIGGER Sgdid_AUR
--
--  After a row in the sgdid table is updated, 
--  write record to update_log table
--
    AFTER UPDATE ON sgdid
    FOR EACH ROW
BEGIN
  IF UPDATING THEN

    IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('SGDID', 'SOURCE_ID', :old.sgdid, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('SGDID', 'BUD_ID', :old.sgdid, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.subclass != :new.subclass)
    THEN
        AuditLog.InsertUpdateLog('SGDID', 'SUBCLASS', :old.sgdid, :old.subclass, :new.subclass, USER);
    END IF;

    IF (:old.sgdid_status != :new.sgdid_status)
    THEN
        AuditLog.InsertUpdateLog('SGDID', 'SGDID_STATUS', :old.sgdid, :old.sgdid_status, :new.sgdid_status, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('SGDID', 'DESCRIPTION', :old.sgdid, :old.description, :new.description, USER);
    END IF;

  END IF;

END Sgdid_AUR;
/
SHOW ERROR
