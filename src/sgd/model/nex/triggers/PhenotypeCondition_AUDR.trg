CREATE OR REPLACE TRIGGER PhenotypeCondition_AUDR
--
--  After a Phenotype_Condition row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON phenotype_condition
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE_CONDITION', 'ANNOTATION_ID', :old.condition_id, :old.annotation_id, :new.annotation_id, USER);
    END IF;

     IF (:old.condition_name != :new.condition_name)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE_CONDITION', 'CONDITION_NAME', :old.condition_id, :old.condition_name, :new.condition_name, USER);
    END IF;

    IF (:old.condition_value != :new.condition_value) 
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE_CONDITION', 'CONDITION_VALUE', :old.condition_id, :old.condition_value, :new.condition_value, USER);
    END IF;

  ELSE

    v_row := :old.condition_id || '[:]' || :old.annotation_id || '[:]' ||
             :old.condition_name || '[:]' || :old.condition_value || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PHENOTYPE_CONDITION', :old.condition_id, v_row, USER);

  END IF;

END PhenotypeCondition_AUDR;
/
SHOW ERROR
