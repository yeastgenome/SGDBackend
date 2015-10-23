CREATE OR REPLACE TRIGGER ReferenceAuthor_AUDR
--
--  After a row in the reference_author table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON reference_author
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_AUTHOR', 'DISPLAY_NAME', :old.reference_author_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_AUTHOR', 'OBJ_URL', :old.reference_author_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_AUTHOR', 'SOURCE_ID', :old.reference_author_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_AUTHOR', 'BUD_ID', :old.reference_author_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_AUTHOR', 'REFERENCE_ID', :old.reference_author_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.orcid IS NULL) AND (:new.orcid IS NOT NULL)) OR ((:old.orcid IS NOT NULL) AND (:new.orcid IS NULL)) OR (:old.orcid != :new.orcid))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_AUTHOR', 'ORCID', :old.reference_author_id, :old.orcid, :new.orcid, USER);
    END IF;

     IF (:old.author_order != :new.author_order)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_AUTHOR', 'AUTHOR_ORDER', :old.reference_author_id, :old.author_order, :new.author_order, USER);
    END IF;

     IF (:old.author_type != :new.author_type)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_AUTHOR', 'AUTHOR_TYPE', :old.reference_author_id, :old.author_type, :new.author_type, USER);
    END IF;

  ELSE

    v_row := :old.reference_author_id || '[:]' || :old.display_name || '[:]' ||
             :old.obj_url || '[:]' || :old.source_id || '[:]' ||
             :old.bud_id || '[:]' || :old.reference_id || '[:]' ||
             :old.orcid || '[:]' || :old.author_order || '[:]' ||
             :old.author_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('REFERENCE_AUTHOR', :old.reference_author_id, v_row, USER);

  END IF;

END ReferenceAuthor_AUDR;
/
SHOW ERROR
