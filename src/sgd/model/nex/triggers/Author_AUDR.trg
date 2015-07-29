CREATE OR REPLACE TRIGGER Author_AUDR
--
--  After a row in the author table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON author
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('AUTHOR', 'FORMAT_NAME', :old.author_id, :old.format_name, :new.format_name, USER);
    END IF;

     IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('AUTHOR', 'DISPLAY_NAME', :old.author_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('AUTHOR', 'OBJ_URL', :old.author_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('AUTHOR', 'SOURCE_ID', :old.author_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('AUTHOR', 'BUD_ID', :old.author_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (((:old.orcid IS NULL) AND (:new.orcid IS NOT NULL)) OR ((:old.orcid IS NOT NULL) AND (:new.orcid IS NULL)) OR (:old.orcid != :new.orcid))
    THEN
        AuditLog.InsertUpdateLog('AUTHOR', 'ORCID', :old.author_id, :old.orcid, :new.orcid, USER);
    END IF;

  ELSE

    v_row := :old.author_id || '[:]' || :old.format_name || '[:]' ||
             :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.orcid || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('AUTHOR', :old.author_id, v_row, USER);

  END IF;

END Author_AUDR;
/
SHOW ERROR
