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

     IF (:old.detail_type != :new.detail_type)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'DETAIL_TYPE', :old.detail_id, :old.detail_type, :new.detail_type, USER);
    END IF;

     IF (:old.detail_name != :new.detail_name)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'DETAIL_NAME', :old.detail_id, :old.detail_name, :new.detail_name, USER);
    END IF;

    IF (:old.detail_value != :new.detail_value) 
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION_DETAIL', 'DETAIL_VALUE', :old.detail_id, :old.detail_value, :new.detail_value, USER);
    END IF;

  ELSE

    v_row := :old.detail_id || '[:]' || :old.annotation_id || '[:]' ||
             :old.detail_type || '[:]' ||
             :old.detail_name || '[:]' || :old.detail_value || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PHENOTYPEANNOTATION_DETAIL', :old.detail_id, v_row, USER);

  END IF;

END PhenotypeannotationDetail_AUDR;
/
SHOW ERROR
