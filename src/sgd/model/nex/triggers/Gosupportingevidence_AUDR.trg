CREATE OR REPLACE TRIGGER Gosupportingevidence_AUDR
--
--  After a row in the gosupportingevidence table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON gosupportingevidence
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('GOSUPPORTINGEVIDENCE', 'ANNOTATION_ID', :old.gosupportingevidence_id, :old.annotation_id, :new.annotation_id, USER);
    END IF;

     IF (:old.group_id != :new.group_id)
    THEN
        AuditLog.InsertUpdateLog('GOSUPPORTINGEVIDENCE', 'GROUP_ID', :old.gosupportingevidence_id, :old.group_id, :new.group_id, USER);
    END IF;

     IF (:old.dbxref_id != :new.dbxref_id)
    THEN
        AuditLog.InsertUpdateLog('GOSUPPORTINGEVIDENCE', 'DBXREF_ID', :old.gosupportingevidence_id, :old.dbxref_id, :new.dbxref_id, USER);
    END IF;

     IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('GOSUPPORTINGEVIDENCE', 'OBJ_URL', :old.gosupportingevidence_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.evidence_type != :new.evidence_type)
    THEN
        AuditLog.InsertUpdateLog('GOSUPPORTINGEVIDENCE', 'EVIDENCE_TYPE', :old.gosupportingevidence_id, :old.evidence_type, :new.evidence_type, USER);
    END IF;

  ELSE

    v_row := :old.gosupportingevidence_id || '[:]' || :old.annotation_id || '[:]' ||
             :old.group_id || '[:]' || :old.dbxref_id || '[:]' ||
             :old.obj_url || '[:]' || :old.evidence_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('GOSUPPORTINGEVIDENCE', :old.gosupportingevidence_id, v_row, USER);

  END IF;

END Gosupportingevidence_AUDR;
/
SHOW ERROR
