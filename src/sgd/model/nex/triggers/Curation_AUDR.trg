CREATE OR REPLACE TRIGGER Curation_AUDR
--
--  After a Curation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON curation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('CURATION', 'DBENTITY_ID', :old.curation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('CURATION', 'SOURCE_ID', :old.curation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('CURATION', 'BUD_ID', :old.curation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.subclass != :new.subclass) 
    THEN
        AuditLog.InsertUpdateLog('CURATION', 'SUBCLASS', :old.curation_id, :old.subclass, :new.subclass, USER);
    END IF;

    IF (:old.curation_task != :new.curation_task)
    THEN
        AuditLog.InsertUpdateLog('CURATION', 'CURATION_TASK', :old.curation_id, :old.curation_task, :new.curation_task, USER);
    END IF;

    IF (((:old.curator_comment IS NULL) AND (:new.curator_comment IS NOT NULL)) OR ((:old.curator_comment IS NOT NULL) AND (:new.curator_comment IS NULL)) OR (:old.curator_comment != :new.curator_comment))
    THEN
        AuditLog.InsertUpdateLog('CURATION', 'CURATOR_COMMENT', :old.curation_id, :old.curator_comment, :new.curator_comment, USER);
    END IF;

  ELSE

    v_row := :old.curation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' || 
             :old.reference_id || '[:]' || :old.bud_id || '[:]' ||
             :old.subclass || '[:]' || :old.curation_task || '[:]' ||
             :old.curator_comment || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('CURATION', :old.curation_id, v_row, USER);

  END IF;

END Curation_AUDR;
/
SHOW ERROR
