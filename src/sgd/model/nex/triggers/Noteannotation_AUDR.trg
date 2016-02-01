CREATE OR REPLACE TRIGGER Noteannotation_AUDR
--
--  After a Noteannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON noteannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF  (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.contig_id IS NULL) AND (:new.contig_id IS NOT NULL)) OR ((:old.contig_id IS NOT NULL) AND (:new.contig_id IS NULL)) OR (:old.contig_id != :new.contig_id))
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'CONTIG_ID', :old.annotation_id, :old.contig_id, :new.contig_id, USER);
    END IF;

    IF (:old.note_type != :new.note_type) 
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'NOTE_TYPE', :old.annotation_id, :old.note_type, :new.note_type, USER);
    END IF;

    IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'DISPLAY_NAME', :old.annotation_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.note != :new.note)
    THEN
        AuditLog.InsertUpdateLog('NOTEANNOTATION', 'NOTE', :old.annotation_id, :old.note, :new.note, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' || 
             :old.reference_id || '[:]' || :old.contig_id || '[:]' ||
             :old.bud_id || '[:]' || :old.note_type || '[:]' || 
             :old.display_name || '[:]' || :old.note || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('NOTEANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Noteannotation_AUDR;
/
SHOW ERROR
