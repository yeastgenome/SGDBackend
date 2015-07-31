CREATE OR REPLACE TRIGGER LocusSummary_AUDR
--
--  After a row in the locus_summary table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON locus_summary
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_SUMMARY', 'SOURCE_ID', :old.summary_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('LOCUS_SUMMARY', 'BUD_ID', :old.summary_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.locus_id != :new.locus_id)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_SUMMARY', 'LOCUS_ID', :old.summary_id, :old.locus_id, :new.locus_id, USER);
    END IF;

    IF (:old.summary_type != :new.summary_type)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_SUMMARY', 'SUMMARY_TYPE', :old.summary_id, :old.summary_type, :new.summary_type, USER);
    END IF;

    IF (:old.summary_order != :new.summary_order)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_SUMMARY', 'SUMMARY_ORDER', :old.summary_id, :old.summary_order, :new.summary_order, USER);
    END IF;

    IF (:old.text != :new.text)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_SUMMARY', 'TEXT', :old.summary_id, :old.text, :new.text, USER);
    END IF;

    IF (:old.html != :new.html)
    THEN
        AuditLog.InsertUpdateLog('LOCUS_SUMMARY', 'HTML', :old.summary_id, :old.html, :new.html, USER);
    END IF;

  ELSE

    v_row := :old.summary_id || '[:]' || :old.source_id || '[:]' ||
             :old.bud_id || '[:]' || :old.locus_id || '[:]' ||
             :old.summary_type || '[:]' || :old.summary_order || '[:]' ||
             :old.text || '[:]' || :old.html || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('LOCUS_SUMMARY', :old.summary_id, v_row, USER);

  END IF;

END LocusSummary_AUDR;
/
SHOW ERROR
