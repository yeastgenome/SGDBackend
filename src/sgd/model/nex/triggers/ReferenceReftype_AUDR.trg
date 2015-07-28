CREATE OR REPLACE TRIGGER ReferenceReftype_AUDR
--
--  After a row in the reference_reftype table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON reference_reftype
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_REFTYPE', 'REFERENCE_ID', :old.reference_reftype_id, :old.reference_id, :new.reference_id, USER);
    END IF;

     IF (:old.reftype_id != :new.reftype_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_REFTYPE', 'REFTYPE_ID', :old.reference_reftype_id, :old.reftype_id, :new.reftype_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_REFTYPE', 'SOURCE_ID', :old.reference_reftype_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.reference_reftype_id || '[:]' || :old.reference_id || '[:]' ||
             :old.reftype_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('REFERENCE_REFTYPE', :old.reference_reftype_id, v_row, USER);

  END IF;

END ReferenceReftype_AUDR;
/
SHOW ERROR
