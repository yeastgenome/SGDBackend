CREATE OR REPLACE TRIGGER ArchLocuschange_AUDR
--
--  After a row in the arch_locuschange table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON arch_locuschange
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

	 IF (:old.locus_id != :new.locus_id)
    THEN
        AuditLog.InsertUpdateLog('ARCH_LOCUSCHANGE', 'LOCUS_ID', :old.change_id, :old.locus_id, :new.locus_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('ARCH_LOCUSCHANGE', 'SOURCE_ID', :old.change_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('ARCH_LOCUSCHANGE', 'BUD_ID', :old.change_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.change_type != :new.change_type)
    THEN
        AuditLog.InsertUpdateLog('ARCH_LOCUSCHANGE', 'CHANGE_TYPE', :old.change_id, :old.change_type, :new.change_type, USER);
    END IF;

    IF (((:old.old_value IS NULL) AND (:new.old_value IS NOT NULL)) OR ((:old.old_value IS NOT NULL) AND (:new.old_value IS NULL)) OR (:old.old_value != :new.old_value))
    THEN
        AuditLog.InsertUpdateLog('ARCH_LOCUSCHANGE', 'OLD_VALUE', :old.change_id, :old.old_value, :new.old_value, USER);
    END IF;

    IF (((:old.new_value IS NULL) AND (:new.new_value IS NOT NULL)) OR ((:old.new_value IS NOT NULL) AND (:new.new_value IS NULL)) OR (:old.new_value != :new.new_value))
    THEN
        AuditLog.InsertUpdateLog('ARCH_LOCUSCHANGE', 'NEW_VALUE', :old.change_id, :old.new_value, :new.new_value, USER);
    END IF;

    IF (:old.date_changed != :new.date_changed)
    THEN
        AuditLog.InsertUpdateLog('ARCH_LOCUSCHANGE', 'DATE_CHANGED', :old.change_id, :old.date_changed, :new.date_changed, USER);
    END IF;

    IF (:old.changed_by != :new.changed_by)
    THEN
        AuditLog.InsertUpdateLog('ARCH_LOCUSCHANGE', 'CHANGED_BY', :old.change_id, :old.changed_by, :new.changed_by, USER);
    END IF;

  ELSE

    v_row := :old.change_id || '[:]' || :old.locus_id || '[:]' || 
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.change_type || '[:]' || :old.old_value || '[:]' || 
             :old.new_value || '[:]' || :old.date_changed || '[:]' ||
             :old.changed_by || '[:]' || :old.date_archived;

    AuditLog.InsertDeleteLog('ARCH_LOCUSCHANGE', :old.change_id, v_row, USER);

  END IF;

END ArchLocuschange_AUDR;
/
SHOW ERROR
