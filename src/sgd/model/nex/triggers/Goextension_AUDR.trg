CREATE OR REPLACE TRIGGER Goextension_AUDR
--
--  After a row in the goextension table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON goextension
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('GOEXTENSION', 'ANNOTATION_ID', :old.goextension_id, :old.annotation_id, :new.annotation_id, USER);
    END IF;

	 IF (:old.group_id != :new.group_id)
    THEN
        AuditLog.InsertUpdateLog('GOEXTENSION', 'GROUP_ID', :old.goextension_id, :old.group_id, :new.group_id, USER);
    END IF;

     IF (:old.dbxref_id != :new.dbxref_id)
    THEN
        AuditLog.InsertUpdateLog('GOEXTENSION', 'DBXREF_ID', :old.goextension_id, :old.dbxref_id, :new.dbxref_id, USER);
    END IF;

     IF (:old.ro_id != :new.ro_id)
    THEN
        AuditLog.InsertUpdateLog('GOEXTENSION', 'RO_ID', :old.goextension_id, :old.ro_id, :new.ro_id, USER);
    END IF;

     IF (:old.operator != :new.operator)
    THEN
        AuditLog.InsertUpdateLog('GOEXTENSION', 'OPERATOR', :old.goextension_id, :old.operator, :new.operator, USER);
    END IF;

  ELSE

    v_row := :old.goextension_id || '[:]' || :old.annotation_id || '[:]' ||
		  	 :old.group_id || '[:]' || :old.dbxref_id || '[:]' ||
             :old.ro_id || '[:]' || :old.operator || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('GOEXTENSION', :old.goextension_id, v_row, USER);

  END IF;

END Goextension_AUDR;
/
SHOW ERROR
