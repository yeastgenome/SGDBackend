CREATE OR REPLACE TRIGGER PhenotypeannotationDetail_AUDR
--
--  After a Phenotypeannotation_Detail row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON phenotypeannotation_detail
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'ANNOTATION_ID', :old.detail_id, :old.annotation_id, :new.annotation_id, USER);
    END IF;

     IF (:old.category != :new.category)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'CATEGORY', :old.detail_id, :old.category, :new.category, USER);
    END IF;

     IF (:old.detail_type != :new.detail_type)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'DETAIL_TYPE', :old.detail_id, :old.detail_type, :new.detail_type, USER);
    END IF;

     IF (:old.detail_value != :new.detail_value)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'DETAIL_VALUE', :old.detail_id, :old.detail_value, :new.detail_value, USER);
    END IF;

    IF (((:old.detail_number IS NULL) AND (:new.detail_number IS NOT NULL)) OR ((:old.detail_number IS NOT NULL) AND (:new.detail_number IS NULL)) OR (:old.detail_number != :new.detail_number))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'DETAIL_NUMBER', :old.detail_id, :old.detail_number, :new.detail_number, USER);
    END IF;

    IF (((:old.detail_unit IS NULL) AND (:new.detail_unit IS NOT NULL)) OR ((:old.detail_unit IS NOT NULL) AND (:new.detail_unit IS NULL)) OR (:old.detail_unit != :new.detail_unit))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'DETAIL_UNIT', :old.detail_id, :old.detail_unit, :new.detail_unit, USER);
    END IF;

  ELSE

    v_row := :old.detail_id || '[:]' || :old.annotation_id || '[:]' ||
             :old.category || '[:]' || :old.detail_type || '[:]' ||
             :old.detail_value || '[:]' || :old.detail_number || '[:]' ||
             :old.detail_unit || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PHENOTYPEANNOTATION_DETAIL', :old.detail_id, v_row, USER);

  END IF;

END PhenotypeannotationDetail_AUDR;
/
SHOW ERROR
