CREATE OR REPLACE TRIGGER ColleagueLocus_AUDR
--
--  After a row in the colleague_locus table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON colleague_locus
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.colleague_id != :new.colleague_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_LOCUS', 'COLLEAGUE_ID', :old.colleague_locus_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

     IF (:old.locus_id != :new.locus_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_LOCUS', 'LOCUS_ID', :old.colleague_locus_id, :old.locus_id, :new.locus_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_LOCUS', 'SOURCE_ID', :old.colleague_locus_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.colleague_locus_id || '[:]' || :old.colleague_id || '[:]' ||
             :old.locus_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('COLLEAGUE_LOCUS', :old.colleague_locus_id, v_row, USER);

  END IF;

END ColleagueLocus_AUDR;
/
SHOW ERROR
