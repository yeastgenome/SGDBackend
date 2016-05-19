CREATE OR REPLACE TRIGGER Dosupportingevidence_AUDR
--
--  After a row in the dosupportingevidence table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dosupportingevidence
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('DOSUPPORTINGEVIDENCE', 'ANNOTATION_ID', :old.dosupportingevidence_id, :old.annotation_id, :new.annotation_id, USER);
    END IF;

     IF (:old.group_id != :new.group_id)
    THEN
        AuditLog.InsertUpdateLog('DOSUPPORTINGEVIDENCE', 'GROUP_ID', :old.dosupportingevidence_id, :old.group_id, :new.group_id, USER);
    END IF;

     IF (:old.dbxref_id != :new.dbxref_id)
    THEN
        AuditLog.InsertUpdateLog('DOSUPPORTINGEVIDENCE', 'DBXREF_ID', :old.dosupportingevidence_id, :old.dbxref_id, :new.dbxref_id, USER);
    END IF;

     IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('DOSUPPORTINGEVIDENCE', 'OBJ_URL', :old.dosupportingevidence_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.evidence_type != :new.evidence_type)
    THEN
        AuditLog.InsertUpdateLog('DOSUPPORTINGEVIDENCE', 'EVIDENCE_TYPE', :old.dosupportingevidence_id, :old.evidence_type, :new.evidence_type, USER);
    END IF;

  ELSE

    v_row := :old.dosupportingevidence_id || '[:]' || :old.annotation_id || '[:]' ||
             :old.group_id || '[:]' || :old.dbxref_id || '[:]' ||
             :old.obj_url || '[:]' || :old.evidence_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DOSUPPORTINGEVIDENCE', :old.dosupportingevidence_id, v_row, USER);

  END IF;

END Dosupportingevidence_AUDR;
/
SHOW ERROR
