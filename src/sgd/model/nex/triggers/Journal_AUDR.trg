CREATE OR REPLACE TRIGGER Journal_AUDR
--
--  After a row in the journal table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON journal
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('JOURNAL', 'FORMAT_NAME', :old.journal_id, :old.format_name, :new.format_name, USER);
    END IF;

     IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('JOURNAL', 'DISPLAY_NAME', :old.journal_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('JOURNAL', 'OBJ_URL', :old.journal_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('JOURNAL', 'SOURCE_ID', :old.journal_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('JOURNAL', 'BUD_ID', :old.journal_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (((:old.med_abbr IS NULL) AND (:new.med_abbr IS NOT NULL)) OR ((:old.med_abbr IS NOT NULL) AND (:new.med_abbr IS NULL)) OR (:old.med_abbr != :new.med_abbr))
    THEN
        AuditLog.InsertUpdateLog('Journal', 'MED_ABBR', :old.journal_id, :old.med_abbr, :new.med_abbr, USER);
    END IF;

    IF (((:old.title IS NULL) AND (:new.title IS NOT NULL)) OR ((:old.title IS NOT NULL) AND (:new.title IS NULL)) OR (:old.title != :new.title))
    THEN
        AuditLog.InsertUpdateLog('Journal', 'TITLE', :old.journal_id, :old.title, :new.title, USER);
    END IF;

    IF (((:old.issn_print IS NULL) AND (:new.issn_print IS NOT NULL)) OR ((:old.issn_print IS NOT NULL) AND (:new.issn_print IS NULL)) OR (:old.issn_print != :new.issn_print))
    THEN
        AuditLog.InsertUpdateLog('Journal', 'ISSN_PRINT', :old.journal_id, :old.issn_print, :new.issn_print, USER);
    END IF;

    IF (((:old.issn_electronic IS NULL) AND (:new.issn_electronic IS NOT NULL)) OR ((:old.issn_electronic IS NOT NULL) AND (:new.issn_electronic IS NULL)) OR (:old.issn_electronic != :new.issn_electronic))
    THEN
        AuditLog.InsertUpdateLog('Journal', 'ISSN_ELECTRONIC', :old.journal_id, :old.issn_electronic, :new.issn_electronic, USER);
    END IF;

  ELSE

    v_row := :old.journal_id || '[:]' || :old.format_name || '[:]' ||
             :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.med_abbr || '[:]' || :old.title || '[:]' ||
             :old.issn_print || '[:]' || :old.issn_electronic || '[:]' || 
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('JOURNAL', :old.journal_id, v_row, USER);

  END IF;

END Journal_AUDR;
/
SHOW ERROR
