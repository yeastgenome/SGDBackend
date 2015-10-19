CREATE OR REPLACE TRIGGER ReferenceUnlink_AUDR
--
--  After a row in the reference_unlink table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON reference_unlink
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.reference_id != :new.reference_id )
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_UNLINK', 'REFERENCE_ID', :old.reference_unlink_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.dbentity_id != :new.dbentity_id) 
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_UNLINK', 'DBENTITY_ID', :old.reference_unlink_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id)) 
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_UNLINK', 'BUD_ID', :old.reference_unlink_id, :old.bud_id, :new.bud_id, USER);
    END IF;

  ELSE

    v_row := :old.reference_unlink_id || '[:]' || :old.reference_id || '[:]' || 
             :old.dbentity_id || '[:]' || :old.bud_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('REFERENCE_UNLINK', :old.reference_unlink_id, v_row, USER);

  END IF;

END ReferenceUnlink_AUDR;
/
SHOW ERROR
