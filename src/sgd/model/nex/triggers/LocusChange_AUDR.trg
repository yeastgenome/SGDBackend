CREATE OR REPLACE TRIGGER LocusChange_AUDR
--
--  After a row in the locus_change table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON locus_change
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

	 IF (:old.locus_id != :new.locus_id)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_CHANGE', 'LOCUS_ID', :old.change_id, :old.locus_id, :new.locus_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_CHANGE', 'SOURCE_ID', :old.change_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('LOCUS_CHANGE', 'BUD_ID', :old.change_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.change_type != :new.change_type)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_CHANGE', 'CHANGE_TYPE', :old.change_id, :old.change_type, :new.change_type, USER);
    END IF;

    IF (((:old.old_value IS NULL) AND (:new.old_value IS NOT NULL)) OR ((:old.old_value IS NOT NULL) AND (:new.old_value IS NULL)) OR (:old.old_value != :new.old_value))
    THEN
        AuditLog.InsertUpdateLog('LOCUS_CHANGE', 'OLD_VALUE', :old.change_id, :old.old_value, :new.old_value, USER);
    END IF;

    IF (((:old.new_value IS NULL) AND (:new.new_value IS NOT NULL)) OR ((:old.new_value IS NOT NULL) AND (:new.new_value IS NULL)) OR (:old.new_value != :new.new_value))
    THEN
        AuditLog.InsertUpdateLog('LOCUS_CHANGE', 'NEW_VALUE', :old.change_id, :old.new_value, :new.new_value, USER);
    END IF;

    IF (:old.date_change_made != :new.date_change_made)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_CHANGE', 'DATE_CHANGE_MADE', :old.change_id, :old.date_change_made, :new.date_change_made, USER);
    END IF;

  ELSE

    v_row := :old.change_id || '[:]' || :old.locus_id || '[:]' || 
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.change_type || '[:]' || :old.old_value || '[:]' || 
             :old.new_value || '[:]' || :old.date_change_made || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('LOCUS_CHANGE', :old.change_id, v_row, USER);

  END IF;

END LocusChange_AUDR;
/
SHOW ERROR
