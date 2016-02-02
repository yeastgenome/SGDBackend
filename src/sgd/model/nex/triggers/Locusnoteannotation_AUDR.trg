CREATE OR REPLACE TRIGGER Locusnoteannotation_AUDR
--
--  After a Locusnoteannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON locusnoteannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('LOCUSNOTEANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('LOCUSNOTEANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF  (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('LOCUSNOTEANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('LOCUSNOTEANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('LOCUSNOTEANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.note_type != :new.note_type) 
    THEN
        AuditLog.InsertUpdateLog('LOCUSNOTEANNOTATION', 'NOTE_TYPE', :old.annotation_id, :old.note_type, :new.note_type, USER);
    END IF;

    IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('LOCUSNOTEANNOTATION', 'DISPLAY_NAME', :old.annotation_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.note != :new.note)
    THEN
        AuditLog.InsertUpdateLog('LOCUSNOTEANNOTATION', 'NOTE', :old.annotation_id, :old.note, :new.note, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' || 
             :old.reference_id || '[:]' || 
             :old.bud_id || '[:]' || :old.note_type || '[:]' || 
             :old.display_name || '[:]' || :old.note || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('LOCUSNOTEANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Locusnoteannotation_AUDR;
/
SHOW ERROR
