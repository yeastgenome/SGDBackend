CREATE OR REPLACE TRIGGER PathwaySummary_AUDR
--
--  After a row in the pathway_summary table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON pathway_summary
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
    v_part1       delete_log.deleted_row%TYPE;
    v_part2       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_SUMMARY', 'SOURCE_ID', :old.summary_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_SUMMARY', 'BUD_ID', :old.summary_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.pathway_id != :new.pathway_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_SUMMARY', 'PATHWAY_ID', :old.summary_id, :old.pathway_id, :new.pathway_id, USER);
    END IF;

    IF (:old.summary_type != :new.summary_type)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_SUMMARY', 'SUMMARY_TYPE', :old.summary_id, :old.summary_type, :new.summary_type, USER);
    END IF;

    IF (:old.text != :new.text)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_SUMMARY', 'TEXT', :old.summary_id, :old.text, :new.text, USER);
    END IF;

    IF (:old.html != :new.html)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_SUMMARY', 'HTML', :old.summary_id, :old.html, :new.html, USER);
    END IF;

  ELSE

    v_part1 := :old.summary_id || '[:]' || :old.source_id || '[:]' ||
             :old.bud_id || '[:]' || :old.pathway_id || '[:]' ||
             :old.summary_type || '[:]' || 
             :old.date_created || '[:]' || :old.created_by;

    v_part2 := concat(concat(v_part1, '[:]'), :old.text);

    v_row := concat(concat(v_part2, '[:]'), :old.html);

    AuditLog.InsertDeleteLog('PATHWAY_SUMMARY', :old.summary_id, v_row, USER);

  END IF;

END PathwaySummary_AUDR;
/
SHOW ERROR
