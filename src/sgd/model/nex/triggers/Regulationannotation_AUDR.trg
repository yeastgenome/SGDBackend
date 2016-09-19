CREATE OR REPLACE TRIGGER Regulationannotation_AUDR
--
--  After a Regulationannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON regulationannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

    IF (:old.target_id != :new.target_id)
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'TARGET_ID', :old.annotation_id, :old.target_id, :new.target_id, USER);
    END IF;

    IF (:old.regulator_id != :new.regulator_id)
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'REGULATOR_ID', :old.annotation_id, :old.regulator_id, :new.regulator_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF  (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.eco_id != :new.eco_id) 
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'ECO_ID', :old.annotation_id, :old.eco_id, :new.eco_id, USER);
    END IF;

    IF (:old.regulator_type != :new.regulator_type)
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'REGULATOR_TYPE', :old.annotation_id, :old.regulator_type, :new.regulator_type, USER);
    END IF;

    IF (:old.regulation_type != :new.regulation_type)
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'REGULATION_TYPE', :old.annotation_id, :old.regulation_type, :new.regulation_type, USER);
    END IF;

    IF (((:old.direction IS NULL) AND (:new.direction IS NOT NULL)) OR ((:old.direction IS NOT NULL) AND (:new.direction IS NULL)) OR (:old.direction != :new.direction))
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'DIRECTION', :old.annotation_id, :old.direction, :new.direction, USER);
    END IF;

    IF (((:old.happens_during IS NULL) AND (:new.happens_during IS NOT NULL)) OR ((:old.happens_during IS NOT NULL) AND (:new.happens_during IS NULL)) OR (:old.happens_during != :new.happens_during))
    THEN
        AuditLog.InsertUpdateLog('REGULATIONANNOTATION', 'HAPPENS_DURING', :old.annotation_id, :old.happens_during, :new.happens_during, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.target_id || '[:]' ||
             :old.regulator_id || '[:]' || :old.source_id || '[:]' ||
             :old.taxonomy_id || '[:]' || :old.reference_id || '[:]' ||
             :old.eco_id || '[:]' || :old.regulator_type || '[:]' ||
             :old.regulation_type || '[:]' || :old.direction || '[:]' ||
             :old.happens_during || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('REGULATIONANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Regulationannotation_AUDR;
/
SHOW ERROR
