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

     IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_REFTYPE', 'DISPLAY_NAME', :old.reference_reftype_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_REFTYPE', 'OBJ_URL', :old.reference_reftype_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_REFTYPE', 'SOURCE_ID', :old.reference_reftype_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_REFTYPE', 'BUD_ID', :old.reference_reftype_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_REFTYPE', 'REFERENCE_ID', :old.reference_reftype_id, :old.reference_id, :new.reference_id, USER);
    END IF;

  ELSE

    v_row := :old.reference_reftype_id || '[:]' || :old.display_name || '[:]' ||
             :old.obj_url || '[:]' || :old.source_id || '[:]' ||
             :old.bud_id || '[:]' || :old.reference_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('REFERENCE_REFTYPE', :old.reference_reftype_id, v_row, USER);

  END IF;

END ReferenceReftype_AUDR;
/
SHOW ERROR
