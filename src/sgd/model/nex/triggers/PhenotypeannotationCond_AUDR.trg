CREATE OR REPLACE TRIGGER PhenotypeannotationCond_AUDR
--
--  After a Phenotypeannotation_Cond row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON phenotypeannotation_cond
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_COND', 'ANNOTATION_ID', :old.condition_id, :old.annotation_id, :new.annotation_id, USER);
    END IF;

     IF (:old.condition_type != :new.condition_type)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_COND', 'CONDITION_TYPE', :old.condition_id, :old.condition_type, :new.condition_type, USER);
    END IF;

     IF (:old.condition_name != :new.condition_name)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_COND', 'CONDITION_NAME', :old.condition_id, :old.condition_name, :new.condition_name, USER);
    END IF;

     IF (((:old.condition_value IS NULL) AND (:new.condition_value IS NOT NULL)) OR ((:old.condition_value IS NOT NULL) AND (:new.condition_value IS NULL)) OR (:old.condition_value != :new.condition_value))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_COND', 'CONDITION_VALUE', :old.condition_id, :old.condition_value, :new.condition_value, USER);
    END IF;

     IF (((:old.condition_unit IS NULL) AND (:new.condition_unit IS NOT NULL)) OR ((:old.condition_unit IS NOT NULL) AND (:new.condition_unit IS NULL)) OR (:old.condition_unit != :new.condition_unit))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_COND', 'CONDITION_UNIT', :old.condition_id, :old.condition_unit, :new.condition_unit, USER);
    END IF;

  ELSE

    v_row := :old.condition_id || '[:]' || :old.annotation_id || '[:]' ||
             :old.condition_type || '[:]' || :old.condition_name || '[:]' || 
             :old.condition_value || '[:]' || :old.condition_unit || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PHENOTYPEANNOTATION_COND', :old.condition_id, v_row, USER);

  END IF;

END PhenotypeannotationCond_AUDR;
/
SHOW ERROR
