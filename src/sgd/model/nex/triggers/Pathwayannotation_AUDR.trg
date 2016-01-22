CREATE OR REPLACE TRIGGER Pathwayannotation_AUDR
--
--  After a Pathwayannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON pathwayannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAYANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAYANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PATHWAYANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF  (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAYANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAYANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.pathway_id != :new.pathway_id) 
    THEN
        AuditLog.InsertUpdateLog('PATHWAYANNOTATION', 'PATHWAY_ID', :old.annotation_id, :old.pathway_id, :new.pathway_id, USER);
    END IF;

    IF (((:old.ec_id IS NULL) AND (:new.ec_id IS NOT NULL)) OR ((:old.ec_id IS NOT NULL) AND (:new.ec_id IS NULL)) OR (:old.ec_id != :new.ec_id))
    THEN
        AuditLog.InsertUpdateLog('PATHWAYANNOTATION', 'EC_ID', :old.annotation_id, :old.ec_id, :new.ec_id, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.taxonomy_id || '[:]' || :old.reference_id || '[:]' ||
             :old.pathway_id || '[:]' || :old.ec_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PATHWAYANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Pathwayannotation_AUDR;
/
SHOW ERROR
