CREATE OR REPLACE TRIGGER StrainSummary_AUDR
--
--  After a row in the strain_summary table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON strain_summary
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('STRAIN_SUMMARY', 'SOURCE_ID', :old.summary_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('STRAIN_SUMMARY', 'BUD_ID', :old.summary_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.strain_id != :new.strain_id)
    THEN
        AuditLog.InsertUpdateLog('STRAIN_SUMMARY', 'STRAIN_ID', :old.summary_id, :old.strain_id, :new.strain_id, USER);
    END IF;

    IF (:old.summary_type != :new.summary_type)
    THEN
        AuditLog.InsertUpdateLog('STRAIN_SUMMARY', 'SUMMARY_TYPE', :old.summary_id, :old.summary_type, :new.summary_type, USER);
    END IF;

    IF (:old.text != :new.text)
    THEN
        AuditLog.InsertUpdateLog('STRAIN_SUMMARY', 'TEXT', :old.summary_id, :old.text, :new.text, USER);
    END IF;

    IF (:old.html != :new.html)
    THEN
        AuditLog.InsertUpdateLog('STRAIN_SUMMARY', 'HTML', :old.summary_id, :old.html, :new.html, USER);
    END IF;

  ELSE

    v_row := :old.summary_id || '[:]' || :old.source_id || '[:]' ||
             :old.bud_id || '[:]' || :old.strain_id || '[:]' ||
             :old.summary_type || '[:]' || 
             :old.text || '[:]' || :old.html || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('STRAIN_SUMMARY', :old.summary_id, v_row, USER);

  END IF;

END StrainSummary_AUDR;
/
SHOW ERROR
