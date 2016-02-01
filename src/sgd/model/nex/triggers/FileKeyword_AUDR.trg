CREATE OR REPLACE TRIGGER FileKeyword_AUDR
--
--  After a row in the file_keyword table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON file_keyword
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.file_id != :new.file_id)
    THEN
        AuditLog.InsertUpdateLog('FILE_KEYWORD', 'FILE_ID', :old.file_keyword_id, :old.file_id, :new.file_id, USER);
    END IF;

     IF (:old.keyword_id != :new.keyword_id)
    THEN
        AuditLog.InsertUpdateLog('FILE_KEYWORD', 'KEYWORD_ID', :old.file_keyword_id, :old.keyword_id, :new.keyword_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('FILE_KEYWORD', 'SOURCE_ID', :old.file_keyword_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.file_keyword_id || '[:]' || :old.file_id || '[:]' ||
             :old.keyword_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('FILE_KEYWORD', :old.file_keyword_id, v_row, USER);

  END IF;

END FileKeyword_AUDR;
/
SHOW ERROR
