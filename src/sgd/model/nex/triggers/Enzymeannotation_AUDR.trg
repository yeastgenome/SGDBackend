CREATE OR REPLACE TRIGGER Enzymeannotation_AUDR
--
--  After a Enzymeannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON enzymeannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('ENZYMEANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('ENZYMEANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('ENZYMEANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF  (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('ENZYMEANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('ENZYMEANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.ec_id != :new.ec_id) 
    THEN
        AuditLog.InsertUpdateLog('ENZYMEANNOTATION', 'EC_ID', :old.annotation_id, :old.ec_id, :new.ec_id, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' || 
             :old.reference_id || '[:]' || :old.bud_id || '[:]' ||
             :old.ec_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('ENZYMEANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Enzymeannotation_AUDR;
/
SHOW ERROR
