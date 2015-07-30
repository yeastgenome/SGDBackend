CREATE OR REPLACE TRIGGER ColleagueKeyword_AUDR
--
--  After a row in the colleague_keyword table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON colleague_keyword
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.colleague_id != :new.colleague_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_KEYWORD', 'COLLEAGUE_ID', :old.colleague_keyword_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

     IF (:old.keyword_id != :new.keyword_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_KEYWORD', 'KEYWORD_ID', :old.colleague_keyword_id, :old.keyword_id, :new.keyword_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_KEYWORD', 'SOURCE_ID', :old.colleague_keyword_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.colleague_keyword_id || '[:]' || :old.colleague_id || '[:]' ||
             :old.keyword_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('COLLEAGUE_KEYWORD', :old.colleague_keyword_id, v_row, USER);

  END IF;

END ColleagueKeyword_AUDR;
/
SHOW ERROR
