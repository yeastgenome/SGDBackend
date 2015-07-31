CREATE OR REPLACE TRIGGER ColleagueReference_AUDR
--
--  After a row in the colleague_reference table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON colleague_reference
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.colleague_id != :new.colleague_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_REFERENCE', 'COLLEAGUE_ID', :old.colleague_reference_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

     IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_REFERENCE', 'REFERENCE_ID', :old.colleague_reference_id, :old.reference_id, :new.reference_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_REFERENCE', 'SOURCE_ID', :old.colleague_reference_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.colleague_reference_id || '[:]' || :old.colleague_id || '[:]' ||
             :old.reference_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('COLLEAGUE_REFERENCE', :old.colleague_reference_id, v_row, USER);

  END IF;

END ColleagueReference_AUDR;
/
SHOW ERROR
