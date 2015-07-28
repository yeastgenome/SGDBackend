CREATE OR REPLACE TRIGGER ReferenceCorrection_AUDR
--
--  After a row in the reference_correction table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON reference_correction
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_CORRECTION', 'SOURCE_ID', :old.reference_correction_id, :old.source_id, :new.source_id, USER);
    END IF;

	 IF (:old.parent_id != :new.parent_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_CORRECTION', 'PARENT_ID', :old.reference_correction_id, :old.parent_id, :new.parent_id, USER);
    END IF;

     IF (:old.child_id != :new.child_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_CORRECTION', 'CHILD_ID', :old.reference_correction_id, :old.child_id, :new.child_id, USER);
    END IF;

    IF (:old.correction_type != :new.correction_type)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_CORRECTION', 'CORRECTION_TYPE', :old.reference_correction_id, :old.correction_type, :new.correction_type, USER);
    END IF;

  ELSE

    v_row := :old.reference_correction_id || '[:]' || :old.source_id || '[:]' ||
		  	 :old.parent_id || '[:]' || :old.child_id || '[:]' || 
             :old.correction_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('REFERENCE_CORRECTION', :old.reference_correction_id, v_row, USER);

  END IF;

END ReferenceCorrection_AUDR;
/
SHOW ERROR
