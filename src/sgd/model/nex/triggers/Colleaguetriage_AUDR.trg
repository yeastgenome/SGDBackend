CREATE OR REPLACE TRIGGER Colleaguetriage_AUDR
--
--  After a Curation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON colleaguetriage
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
    v_part       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.triage_type != :new.triage_type)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUETRIAGE', 'TRIAGE_TYPE', :old.curation_id, :old.triage_type, :new.triage_type, USER);
    END IF;

    IF (((:old.colleague_id IS NULL) AND (:new.colleague_id IS NOT NULL)) OR ((:old.colleague_id IS NOT NULL) AND (:new.colleague_id IS NULL)) OR (:old.colleague_id != :new.colleague_id))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUETRIAGE', 'COLLEAGUE_ID', :old.curation_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

    IF (((:old.colleague_data IS NULL) AND (:new.colleague_data IS NOT NULL)) OR ((:old.colleague_data IS NOT NULL) AND (:new.colleague_data IS NULL)) OR (:old.colleague_data != :new.colleague_data))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUETRIAGE', 'COLLEAGUE_DATA', :old.curation_id, :old.colleague_data, :new.colleague_data, USER);
    END IF;

  ELSE

    v_part := :old.curation_id || '[:]' || :old.triage_type || '[:]' ||
             :old.colleague_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    v_row := concat(concat(v_part, '[:]'), :old.colleague_data);

    AuditLog.InsertDeleteLog('COLLEAGUETRIAGE', :old.curation_id, v_row, USER);

  END IF;

END Colleaguetriage_AUDR;
/
SHOW ERROR
