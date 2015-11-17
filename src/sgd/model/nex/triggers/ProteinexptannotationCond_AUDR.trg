CREATE OR REPLACE TRIGGER ProteinexptannotationCond_AUDR
--
--  After a Proteinexptannotation_Cond row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON proteinexptannotation_cond
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION_COND', 'ANNOTATION_ID', :old.condition_id, :old.annotation_id, :new.annotation_id, USER);
    END IF;

     IF (:old.group_id != :new.group_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION_COND', 'GROUP_ID', :old.condition_id, :old.group_id, :new.group_id, USER);
    END IF;

     IF (:old.condition_class != :new.condition_class)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION_COND', 'CONDITION_CLASS', :old.condition_id, :old.condition_class, :new.condition_class, USER);
    END IF;

     IF (:old.condition_type != :new.condition_type)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION_COND', 'CONDITION_TYPE', :old.condition_id, :old.condition_type, :new.condition_type, USER);
    END IF;

     IF (:old.condition_value != :new.condition_value)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION_COND', 'CONDITION_VALUE', :old.condition_id, :old.condition_value, :new.condition_value, USER);
    END IF;

    IF (((:old.condition_unit IS NULL) AND (:new.condition_unit IS NOT NULL)) OR ((:old.condition_unit IS NOT NULL) AND (:new.condition_unit IS NULL)) OR (:old.condition_unit != :new.condition_unit))
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION_COND', 'CONDITION_UNIT', :old.condition_id, :old.condition_unit, :new.condition_unit, USER);
    END IF;

  ELSE

    v_row := :old.condition_id || '[:]' || :old.annotation_id || '[:]' ||
             :old.group_id || '[:]' || :old.condition_class || '[:]' || 
             :old.condition_type || '[:]' || :old.condition_value || '[:]' || 
             :old.condition_unit || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PROTEINEXPTANNOTATION_COND', :old.condition_id, v_row, USER);

  END IF;

END ProteinexptannotationCond_AUDR;
/
SHOW ERROR
